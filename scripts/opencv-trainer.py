    #!/usr/bin/env python

    import sys
    import cv2, os, threading, logging, time
    import glob
    from face_helper import Face_Helper

    fh = Face_Helper()

    if __name__ == "__main__":

        skipCheck=False

        if len(sys.argv) >= 3:
            nbr = sys.argv[1]
            image_path = sys.argv[2]


            if len(sys.argv) >= 4 and sys.argv[3] == '-skipCheck':
                skipCheck= True

            file_list = []

            if os.path.exists(image_path):

                if os.path.isfile(image_path):
                    file_list.append(image_path)
                    fh.train_pictures(file_list, int(nbr), skipCheck)

                elif os.path.isdir(image_path):
                    file_list= glob.glob(image_path +"/*")
                    fh.train_pictures(file_list, int(nbr), skipCheck)

                elif glob.glob(image_path).length:
                    file_list= glob.glob(image_path)
                    fh.train_pictures(file_list, int(nbr), skipCheck)

                else:
                    print "file not found"

            fh.save()

        else:
            print "usage: <script> <nbr> <file/dir>"
