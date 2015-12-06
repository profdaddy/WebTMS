import paramiko
import sys

class JSONUpload:

    host = "dunx1.irt.drexel.edu"
    port = 22
    password = "Myd0gisl1z"
    username = "bks59"
    filename = "webtms.json"

    def upload(self):

        transport = paramiko.Transport((self.host, self.port))

        transport.connect(username = self.username, password = self.password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        path = './public_html/webtms/' + self.filename
        sftp.put(self.filename, path)

        sftp.close()
        transport.close()
        print 'Upload done.'

    def __init__(self, filename):
        self.filename = filename

    def main(argv=sys.argv):
        # parse command line
        try:
            filename = argv[1]
            myUploader = None

            JSONUpload(filename).upload()
        except Exception:
            print("Found an error creating an upload" )

    if __name__ == "__main__":
        main()