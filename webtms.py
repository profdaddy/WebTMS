from bs4 import BeautifulSoup
from urllib import urlopen
#from urllib.error import HTTPError
from urllib2 import HTTPError
import json
import re
from operator import itemgetter, attrgetter
from jsonUpload import JSONUpload


edltURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDM0NToAa3xJwchcDSxCKgIgVDM11DcwD9ZmnspAAAAA%3D%3D&sp=ST&sp=SEDLT&sp=15'
crtvURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDM0NToAa3xJwchcDSxCKgIgVDM11DcwD9ZmnspAAAAA%3D%3D&sp=ST&sp=SCRTV&sp=15'
ellURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDM0NToAa3xJwchcDSxCKgIgVDM11DcwD9ZmnspAAAAA%3D%3D&sp=ST&sp=SELL&sp=15'
aeodFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDM0NToAa3xJwchcDSxCKgIgVDM11DcwD9ZmnspAAAAA%3D%3D&sp=ST&sp=SEHRD&sp=15'
educURLFall ='https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDM0NToAa3xJwchcDSxCKgIgVDM11DcwD9ZmnspAAAAA%3D%3D&sp=ST&sp=SEDUC&sp=15'

TMS_URLS = [crtvURLFall, edltURLFall, ellURLFall, aeodFall]

# first stab at this, add a second list to scan a list of courses and just pull certain courses.
# each entry is a list with a URL as key, list of course numbers to grab as the value
PARTIAL_TMS_URLS = [] # [ [educURLFall, ['325', '525']] ]

# i'm a regex to get digits from the string with max and current enrollments
DIGIT_REGEX = re.compile('\d+')

# column headings from WebTMS
COURSE_KEYS = ['subjectCode', 'courseNum', 'type', 'method', 'section', 'crn', 'title', 'days/time', 'days', 'time', 'instructor']

# some courses have labs. those have an additional two columns for the lab days and time. adjust for that with this
# list of course headings
COURSE_WITH_LAB_KEYS = ['subjectCode', 'courseNum', 'type', 'method', 'section', 'crn', 'title', 'days/time', 'days', 'time', 'lab_days', 'lab_time', 'instructor']


courseArray = []

def getTableRows(url):
    """scrape tables for course info"""
    try:
        html = urlopen(url)
    except HTTPError as e:
        print("HTTPError"  + e)
        return None
    try:
        bsObj = BeautifulSoup(html.read())
        
        # in best case, i'd grab .even and .odd tr classes at same time.
        # can't do that, so append the two lists
        oddrows = bsObj.findAll("tr", {"class":"odd"})
        evenrows = bsObj.findAll("tr", {"class":"even"})
        rows = oddrows + evenrows
    except AttributeError as e:
        print("Tripped AttributeError" + e)
        return None
    return rows
    
def extractCourseInfo(tableRows, courseNumbers=None, file=None):
    """go through a list of table rows containing <td> info for a course and extrct the important stuff"""
    courseInfo = []
    for row in tableRows:
        courseRows = row.findAll("td")
        
        # currently, the second TD contains the course number. 
        # only include the course if it matches a course number we're looking for
        if courseNumbers is not None:
            if not courseRows[1].getText().strip() in courseNumbers):
                continue
            else:
                print("Looking at course number " + courseRows[1].getText().strip())
                
        for course in courseRows:
             # is this the line with the enrollment numbers?
            if course.p:
                if DIGIT_REGEX.findall(course.p.attrs["title"]):
                    maxEnrollment, enrolled = (DIGIT_REGEX.findall(course.p.attrs["title"]))
                    #print("Max Enrollment: " + maxEnrollment + " Enrolled: " + enrolled)
                else:
                    maxEnrollment, enrolled = "FULL", "FULL"
            infoText = course.getText().strip()
            #if infoText != '' and not "TBD" in infoText:
            # Let's take everything vs. stripping entires with TBD
            if infoText != '':
                courseInfo.append(infoText)

        # if you have all the courseinfo, process to JSON
        if courseInfo[0] != 'TBD':
            print(courseInfo)
            makeCourseJSON(courseInfo, maxEnrollment, enrolled)
        courseInfo = []
    
    return courseArray
            
def makeCourseJSON(courseInfo, maxEnrollment, currentEnrollment):
    """take the scraped list of course info and make into a dictionary. Append that dict onto a courseArray 
        that'll eventually get written out as JSON"""
    jsonDictionary = {}

    my_keys = []
    if len(courseInfo) == len(COURSE_KEYS):
        my_keys = COURSE_KEYS
    else:
        my_keys = COURSE_WITH_LAB_KEYS


    for (key, val) in zip(my_keys, courseInfo):
        jsonDictionary[key] = val
    
    # add the enrollment numbers
    jsonDictionary['maxEnrollment'] = maxEnrollment
    jsonDictionary['currentEnrollment'] = currentEnrollment
    
    
    courseArray.append(jsonDictionary)    
    
def writeJSONHeader(outFile):
    outFile.write("{")
    outFile.write('\t"records": ')
    
def writeJSONFooter(outFile, numberCourses):
    courseRecordString  = '"%s": %d' % ("queryRecordCount" , numberCourses)
    outFile.write(",\n " + courseRecordString)
    totalRecordString = '"%s": %d' % ("totalRecordCount" , numberCourses)
    outFile.write(",\n " + totalRecordString + "\n}")
    
def crawlWebTMS(outputFileName):
    """main function to start crawling. give it an outputfileName to dump
    JSON info to"""    
    
    outFile = open(outputFileName, 'w')
    writeJSONHeader(outFile)
    
    for url in TMS_URLS:
        parsedCourses = getTableRows(url)
        
        if parsedCourses is None:
            print("Title not found")
        else:
            tempArray = extractCourseInfo(parsedCourses)
            print(tempArray)
    
    # LOOP on urls where you just want to pull certain courses        
    for url_dict in PARTIAL_TMS_URLS:
        url, course_numbers = url_dict[0], url_dict[1]
        
        parsedCourses = getTableRows(url)
        
        if parsedCourses is None:
            print("Title not found")
        else:
            tempArray = extractCourseInfo(parsedCourses, courseNumbers=course_numbers)
            print(tempArray)
                
    numberCourses = len(courseArray)

    # sort the array of course objects by subject and course number
    sortedArray = sorted(courseArray, key=itemgetter('subjectCode', 'courseNum'))
        
    outFile.write(json.dumps(sortedArray, indent=2))
        
    writeJSONFooter(outFile, numberCourses)
    outFile.close()

    uploader = JSONUpload(outputFileName)
    uploader.upload()
    
crawlWebTMS('./webtms.json')