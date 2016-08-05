#!/usr/bin/env python
'''
create_ngslibraries.py

Created by Anne Pajon on 02 Apr 2012
Copyright (c) 2012 Cancer Research UK - Cambridge Research Institute.

To connect to LIMS database
ssh uk-cri-lbio08
/opt/local/server/database/mysql/bin/mysql -h uk-cri-lbio04 -u Galaxy -p

Galaxy web api: lib/galaxy/web/api/

Library structure in galaxy: /Group/User/Sample/file.fastq
'''

import optparse
import logging as log
import os, sys
import ConfigParser
from collections import defaultdict
import simplejson, json
import urllib, urllib2
import time
import shutil


def main() :
    # logging configuration
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)

    # get the command line options
    parser = optparse.OptionParser()
    parser.add_option("--lims", dest="lims_server", action="store", help="lims server driver://user[:password]@host[:port]/database (mysql://Galaxy:9414xy@uk-cri-lbio04/cri_general)")
    parser.add_option("--samples", dest="json_filename", action="store", help="json sample full path with filename")
    (options, args) = parser.parse_args()
    try:
        assert options.lims_server
        assert options.json_filename
    except:
        parser.print_help()
        sys.exit( 1 )

    # check env variable define
    if not os.environ['GALAXY_HOME']:
        log.error('Env variable $GALAXY_HOME is not set.')
        sys.exit(1)
        
    # set default galaxy config file universe_wsgi.ini
    galaxy_config_file = os.path.join(os.environ['GALAXY_HOME'] , 'universe_wsgi.ini')
    if not os.path.isfile(galaxy_config_file):
        log.error('Default Galaxy config file %s does not exist.' % galaxy_config_file)
        sys.exit(1)
    os.chdir(os.path.dirname(os.path.abspath(galaxy_config_file)))
    sys.path.append('lib')

    # import galaxy
    from galaxy import eggs
    import pkg_resources
    pkg_resources.require( "SQLAlchemy >= 0.4" )
    from sqlalchemy.ext.sqlsoup import SqlSoup

    # parse galaxy config file
    galaxy_config = ConfigParser.SafeConfigParser()
    galaxy_config.read( os.path.basename( galaxy_config_file ) )

    # get galaxy database connection
    from galaxy.model import mapping
    galaxy_model = mapping.init(galaxy_config.get('app:main','file_path'), galaxy_config.get('app:main', 'database_connection'), create_tables = False)
    galaxy_session = galaxy_model.session

    # set galaxy library import directory
    try:
        lib_import_dir = galaxy_config.get("app:main", "library_import_dir")
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        raise ValueError("galaxy config %s needs library_import_dir to be set." % galaxy_config_file)

    # set storage dir with the galaxy library import directory
    storage_root_folder = os.path.join(lib_import_dir, 'storage')

    # query galaxy db to get all users/groups
    galaxy_groups = galaxy_session.query(galaxy_model.Group)
    all_groups = []
    all_users = {}
    for galaxy_group in galaxy_groups:
        # create library directories for each group on disk
        log.debug("Existing group in galaxy: %s" % galaxy_group.name)
        check_whitespace(galaxy_group.name)
        group_dir = os.path.join(lib_import_dir, galaxy_group.name)
        create_library_dir(group_dir)
        create_library_storage_dir(lib_import_dir, group_dir)
        # create list of all group names
        all_groups.append(galaxy_group.name)
        # query galaxy db to get all users associated to this group
        galaxy_usergroup_associations = galaxy_session.query(galaxy_model.UserGroupAssociation).filter_by(group_id=galaxy_group.id).join(galaxy_model.User).all()
        for galaxy_association in galaxy_usergroup_associations:
            # create library subfolder for each user in this group
            log.debug("Existing user in galaxy: %s" % galaxy_association.user.email)
            check_whitespace(galaxy_association.user.email)
            user_dir = os.path.join(group_dir, galaxy_association.user.email.lower())
            # populate dictionary of all library folders on disk sorted by users
            all_users[galaxy_association.user.email.lower()] = user_dir
            create_library_dir(user_dir)
            create_library_storage_dir(lib_import_dir, user_dir)
        
    # get all samples data from json data file or from lims if it does not exist
    log.info("Reading samples information from %s" % options.json_filename)
    all_samples = defaultdict(lambda: defaultdict(list))
    if os.path.exists(options.json_filename):
        all_samples = simplejson.load(open(options.json_filename, 'r'))
    else:
        # get samples details form lims using its soap api
        from suds.client import Client
        log.getLogger('suds').setLevel(log.INFO)
        lims = Client("http://uk-cri-ldmz02.crnet.org/solexa-ws/SolexaExportBeanWS?wsdl")
        log.debug(lims)
        runs = lims.service.getAllSolexaRuns('true')
        for i in range (0, len(runs)):
            for run in runs[i]:
                for lane in run.sampleLanes:
                    file_locations = lims.service.getFileLocations(lane.sampleProcess_id, 'FILE', 'FASTQ')
                    for j in range (0, len(file_locations)):
                        user_id = lane.userEmail.lower()
                        sample_id = lane.userSampleId.replace(' ', '').replace('/', '_')
                        log.debug("SAMPLE: %s | %s | %s | %s | %s" % (lane.sampleProcess_id, lane.userSampleId, lane.genomicsSampleId, user_id, lane.genome))
                        for file_location in file_locations[j]:
                            if file_location.host == 'uk-cri-lsol03.crnet.org':
                                file_path = "%s/%s" % (file_location.path, file_location.filename)
                                log.debug("   [%s]%s" % (file_location.host, file_path))
                                if not os.path.isfile(file_path):
                                    log.error("File %s does not exists on sol03." % file_path)
                                else:
                                    all_samples[user_id][sample_id].append(file_path)
                                    log.debug("File %s exists on sol03." % file_path)
                            else:
                                log.debug("File on %s" % file_location.host)
        # create json file with all samples
        json_file = open(options.json_filename, 'w')
        simplejson.dump(all_samples, json_file)
        json_file.close()
    
    # read dictionary of all samples sorted by users
    for user, samples in all_samples.iteritems():
        log.debug(user)
        if user in all_users:
            log.debug(all_users[user])
        for sample, files in samples.iteritems():
            # create library subfolder for each sample
            sample_dir = os.path.join(all_users[user], sample.replace(' ', '').replace('/', '_'))
            create_library_dir(sample_dir)
            create_library_storage_dir(lib_import_dir, sample_dir)
            for file in files:
                link_name = os.path.join(sample_dir, os.path.basename(file))
                log.debug(file)
                log.debug(link_name)
                if not os.path.islink(link_name):
                    # create symlinks
                    os.symlink(file, link_name)
                    log.debug("Creating symbolic link: %s" % link_name)
                else:
                    log.debug("Symbolic link %s already exists" % link_name)

    # upload samples into galaxy libraries 
    galaxy_api = GalaxyAccessApi('http://localhost:8080/galaxy', '58f445336457812554c09ae17ac32647')
    for group_folder in os.listdir(lib_import_dir):
        group_folder_path = os.path.join(lib_import_dir, group_folder)        
        if os.path.isdir(group_folder_path) and (group_folder in all_groups):
            log.debug(group_folder)
            # create a library per group
            library_id = galaxy_api.get_datalibrary_id(group_folder)
            log.debug(library_id)
            # get library folder root
            root_folder_id = galaxy_api.get_datafolder_id(library_id, None, '/', None)
            log.debug(root_folder_id)
            # get library contents
            library_contents = galaxy_api.library_contents(library_id)
            log.debug(library_contents)
            for user_folder in os.listdir(group_folder_path):
                user_folder_path = os.path.join(group_folder_path, user_folder)
                if os.path.isdir(user_folder_path) and (user_folder in all_users.keys()):
                    log.debug(user_folder)
                    # create a library folder per user
                    user_folder_id = galaxy_api.get_datafolder_id(library_id, root_folder_id, '/%s' % user_folder, user_folder)
                    log.debug("user folder id: %s" % user_folder_id)
                    for sample_folder in os.listdir(user_folder_path):
                        sample_folder_path = os.path.join(user_folder_path, sample_folder)
                        if os.path.isdir(sample_folder_path):
                            log.debug(sample_folder)
                            # create a library subfolder per sample
                            sample_folder_id = galaxy_api.get_datafolder_id(library_id, user_folder_id, '/%s/%s' % (user_folder, sample_folder), sample_folder)

                            for file in os.listdir(sample_folder_path):
                                log.debug(file)
                                current_files = [f for f in library_contents if f['type'] == 'file'
                                                 and f['name'].startswith("/%s/%s/%s" % (user_folder, sample_folder, file.split('.')[0]))]
                                log.debug(current_files)
                                if len(current_files) > 0:
                                    # move file to storage if alreary uploaded in galaxy
                                    file_path = os.path.join(sample_folder_path, file)
                                    log.debug(file_path)
                                    log.debug(current_files[0]['name'])
                                    storage_folder = sample_folder_path.replace(lib_import_dir, os.path.join(lib_import_dir, 'storage'))
                                    new_file_path = os.path.join(storage_folder, file)
                                    if not os.path.exists(new_file_path):
                                        shutil.move(file_path, storage_folder)
                                        log.debug("Move file %s to storage. Already in galaxy." % file_path)
                                    else:
                                        os.remove(file_path)
                                        log.debug("Remove file %s. Already in galaxy and in storage." % file_path)
                            if len(os.listdir(sample_folder_path)) > 0:
                                # if directory not empty, upload directory contents into library sample folder
                                galaxy_api.upload_directory(library_id, sample_folder_id, '%s/%s/%s' % (group_folder, user_folder, sample_folder), 'hg19')
                                log.debug("Uploading directory %s to galaxy" % sample_folder)

def check_whitespace(str):
    if ' ' in str:
        log.error("String with white space '%s'. Please fix before re-running." % str)
        sys.exit(1)

def create_library_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        log.debug("Creating library dir: %s" % dir)
    else:
        log.debug("Library dir %s already exists" % dir)

def create_library_storage_dir(lib_import_dir, dir):
    storage_dir_path = dir.replace(lib_import_dir, os.path.join(lib_import_dir, 'storage'))
    create_library_dir(storage_dir_path)
    
class GalaxyAccessApi:
    """Simple front end for accessing Galaxy's REST API.
    """
    def __init__(self, galaxy_url, api_key):
        self._base_url = galaxy_url
        self._key = api_key
        self._max_tries = 5

    def _make_url(self, rel_url, params=None):
        if not params:
            params = dict()
        params['key'] = self._key
        vals = urllib.urlencode(params)
        return ("%s%s" % (self._base_url, rel_url), vals)

    def _get(self, url, params=None):
        url, params = self._make_url(url, params)
        num_tries = 0
        while 1:
            response = urllib2.urlopen("%s?%s" % (url, params)).read()
            try:
                out = simplejson.loads(response)
                break
            except ValueError, msg:
                if num_tries > self._max_tries:
                    raise
                time.sleep(3)
                num_tries += 1
        return out

    def _post(self, url, data, params=None, need_return=True):
        url, params = self._make_url(url, params)
        log.debug(url)
        log.debug(data)
        request = urllib2.Request("%s?%s" % (url, params),
                headers = {'Content-Type' : 'application/json'},
                data = simplejson.dumps(data))
        log.debug(request)
        response = urllib2.urlopen(request).read()
        try:
            data = simplejson.loads(response)
        except ValueError:
            if need_return:
                raise
            else:
                data = {}
        return data

    def get_libraries(self):
        return self._get("/api/libraries")

    def show_library(self, library_id):
        return self._get("/api/libraries/%s" % library_id)

    def create_library(self, name, descr="", synopsis=""):
        return self._post("/api/libraries", data = dict(name=name,
            description=descr, synopsis=synopsis))

    def library_contents(self, library_id):
        return self._get("/api/libraries/%s/contents" % library_id)

    def search_library_contents(self, library_id, content_type, content_name):
        return [f for f in self.library_contents(library_id) if f['type'] == content_type and f['name'] == content_name]

    def create_folder(self, library_id, parent_folder_id, name, descr=""):
        return self._post("/api/libraries/%s/contents" % library_id,
                data=dict(create_type="folder", folder_id=parent_folder_id,
                          name=name, description=descr))

    def show_folder(self, library_id, folder_id):
        return self._get("/api/libraries/%s/contents/%s" % (library_id,
            folder_id))

    def upload_directory(self, library_id, folder_id, directory, dbkey,
            access_role='', file_type='auto', link_data_only='link_to_files'):
        """Upload a directory of files with a specific type to Galaxy.
        """
        return self._post("/api/libraries/%s/contents" % library_id,
                data=dict(create_type='file', upload_option='upload_directory',
                    folder_id=folder_id, server_dir=directory,
                    dbkey=dbkey, roles=str(access_role),
                    file_type=file_type, link_data_only=str(link_data_only)),
                need_return=False)

    def upload_from_filesystem(self, library_id, folder_id, fname, dbkey,
            access_role='', file_type='auto', link_data_only='link_to_files'):
        """Upload to Galaxy using 'Upload files from filesystem paths'
        """
        return self._post("/api/libraries/%s/contents" % library_id,
                data=dict(create_type='file', upload_option='upload_paths',
                    folder_id=folder_id, filesystem_paths=fname,
                    dbkey=dbkey, roles=str(access_role),
                    file_type=file_type, link_data_only=str(link_data_only)),
                need_return=False)

    def get_datalibrary_id(self, name):
        """Retrieve a data library with the given name or create new.
        """
        ret_info = None
        for lib_info in self.get_libraries():
            if lib_info["name"].strip() == name.strip():
                ret_info = lib_info
                break
        # need to add a new library
        if ret_info is None:
            ret_info = self.create_library(name)[0]
        return ret_info["id"]

    def get_datafolder_id(self, library_id, parent_folder_id, basename, name):
        """Retrieve a data library folder with the given name or create new
        """
        folders = self.search_library_contents(library_id, 'folder', basename)
        if len(folders) == 0:
            folders = self.create_folder(library_id, parent_folder_id, name)
        return folders[0]['id']
    
if __name__ == '__main__':
    main()
