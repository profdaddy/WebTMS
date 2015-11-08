from bs4 import BeautifulSoup
from urllib import urlopen
from urllib2 import HTTPError
import json
import re
from operator import itemgetter


edltURLWinter = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDUyNToJHhmXlAaYXA0sQiEG1oqmtoBgCbhSKKpgAAAA%3D%3D&sp=ST&sp=SEDLT&sp=14'
crtvURLWinter = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDUyNToJHhmXlAaYXA0sQiEG1oqmtoBgCbhSKKpgAAAA%3D%3D&sp=ST&sp=SCRTV&sp=14'
ellURLWinter = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAAFvzloG1uIhBPjWlVC%2BlKLUiNUcvs6hErzw1qSS3WC8lsSRRLyS1KJcBAhiZGJh9GNgTk0tCMnNTSxhEfLISyxL1iwtz9EECxSWJuQXWPgwcJUAtzvkpQBVCEBU5iXnp%2BsElRZl56TB5l9Ti5EKGOgamioKCEgY2IwNDUyNToJHhmXlAaYXA0sQiEG1oqmtoBgCbhSKKpgAAAA%3D%3D&sp=ST&sp=SELL&sp=14'


edltURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWLOw7CMBAFlyA%2BNaInF8DGSKGhBFGlQeQCS7yKguzg2BtIxYm4GnfAKOKV82beH5gEDyvSndCeejKi9iyedGUbhEZGUZC3MGyUwDiHGZZc1JYYlvkNHyhDa%2BQPBEbr9jnMOSaHu47GYjAMNpW8sK%2Bb6v8fKZQtvCDpnWOYbjcqU1kMTmhMeu7QRylV2Vrtvq1QxdGkAAAA&sp=ST&sp=SEDLT&sp=14'
crtvURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWLOw7CMBAFlyA%2BNaInF8DGSKGhBFGlQeQCS7yKguzg2BtIxYm4GnfAKOKV82beH5gEDyvSndCeejKi9iyedGUbhEZGUZC3MGyUwDiHGZZc1JYYlvkNHyhDa%2BQPBEbr9jnMOSaHu47GYjAMNpW8sK%2Bb6v8fKZQtvCDpnWOYbjcqU1kMTmhMeu7QRylV2Vrtvq1QxdGkAAAA&sp=ST&sp=SCRTV&sp=14'
ellURLFall = 'https://duapp2.drexel.edu/webtms_du/app?component=subjectDetails&page=CollegesSubjects&service=direct&sp=ZH4sIAAAAAAAAADWLOw7CMBAFlyA%2BNaInF8DGSKGhBFGlQeQCS7yKguzg2BtIxYm4GnfAKOKV82beH5gEDyvSndCeejKi9iyedGUbhEZGUZC3MGyUwDiHGZZc1JYYlvkNHyhDa%2BQPBEbr9jnMOSaHu47GYjAMNpW8sK%2Bb6v8fKZQtvCDpnWOYbjcqU1kMTmhMeu7QRylV2Vrtvq1QxdGkAAAA&sp=ST&sp=SELL&sp=14'

TMS_URLS = [crtvURLWinter,edltURLWinter, ellURLWinter]

# i'm a regex to get digits from the string with max and current enrollments
DIGIT_REGEX = re.compile('\d+')

# column headings from WebTMS
COURSE_KEYS = ['subjectCode', 'courseNum', 'type', 'method', 'section', 'crn', 'title', 'instructor']

courseArray = []

def getTableRows(url):
    """scrape tables for course info"""
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bsObj = BeautifulSoup(html.read())
        
        # in best case, i'd grab .even and .odd tr classes at same time.
        # can't do that, so append the two lists
        oddrows = bsObj.findAll("tr", {"class":"odd"})
        evenrows = bsObj.findAll("tr", {"class":"even"})
        rows = oddrows + evenrows
    except AttributeError as e:
        return None
    return rows
    
def extractCourseInfo(tableRows, file=None):
    """go through a list of table rows containing <td> info for a course and extrct the important stuff"""
    courseInfo = []
    for row in tableRows:
        courseRows = row.findAll("td")
        for course in courseRows:
            
            # is this the line with the enrollment numbers?
            if course.p:
                if DIGIT_REGEX.findall(course.p.attrs["title"]):
                    maxEnrollment, enrolled = (DIGIT_REGEX.findall(course.p.attrs["title"]))
                    print("Max Enrollment: " + maxEnrollment + " Enrolled: " + enrolled)
                else:
                    maxEnrollment, enrolled = "FULL", "FULL"
            infoText = course.getText().strip()
            if infoText != '' and not "TBD" in infoText:
                courseInfo.append(infoText)
        
        if courseInfo:
            makeCourseJSON(courseInfo, maxEnrollment, enrolled)
        courseInfo = []
    return courseArray
            
def makeCourseJSON(courseInfo, maxEnrollment, currentEnrollment):
    """take the scraped list of course info and make into a dictionary. Append that dict onto a courseArray 
        that'll eventually get written out as JSON"""
    jsonDictionary = {}
    for (key, val) in zip(COURSE_KEYS, courseInfo):
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
        
        if parsedCourses == None:
            print ("Title not found")
        else:
            tempArray = extractCourseInfo(parsedCourses).sort(key=itemgetter('courseNum'))
            print tempArray
    numberCourses = len(courseArray)
        
    outFile.write(json.dumps(courseArray, indent=2))
        
    writeJSONFooter(outFile, numberCourses)
    
    
crawlWebTMS('./webtms.json')