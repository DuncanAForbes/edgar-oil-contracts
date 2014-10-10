import logging
import re
import os
import shutil
import tempfile
import tarfile
import ftplib

from mrjob.job import MRJob, RawValueProtocol, JSONProtocol

log = logging.getLogger('importer')
HOST = 'ftp.sec.gov'


class MRImportFilings(MRJob):

    INPUT_PROTOCOL = RawValueProtocol
    OUTPUT_PROTOCOL = JSONProtocol

    def mapper(self, x, line):
        fd, tarpath = tempfile.mkstemp()
        os.close(fd)
        dir = tempfile.mkdtemp()

        try:
            ftp = ftplib.FTP(HOST)
            ftp.login('anonymous', '@anonymous')
            with open(tarpath, 'wb') as fh:
                ftp.retrbinary("RETR " + line, fh.write)
            ftp.quit()

            tb = tarfile.open(tarpath, 'r:gz')
            tb.extractall(path=dir)
            for file_name in os.listdir(dir):
                path = os.path.join(dir, file_name)
                fn = '%s:%s' % (line, file_name)
                with open(path, 'r') as fh:
                    #process_filing(fh.read())
                    yield fn, fh.read()
        except EnvironmentError, ee:
            log.exception(ee)
        except Exception, e:
            log.exception(e)
        finally:
            shutil.rmtree(dir)
            os.unlink(tarpath)

    #def reducer(self, key, values):
    #    yield key, values


if __name__ == '__main__':
    MRImportFilings.run()
