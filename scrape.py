import requests
from bs4 import BeautifulSoup
from resizeimage import resizeimage
import time
import os
import re
from PIL import Image
from selenium import webdriver
import random

import unicodedata


scriptDir = os.path.dirname(os.path.abspath(__file__))
picDir = os.path.join(scriptDir,"shoes")
# scrape class has a function for all websites we are gathering data from
class scrape():

    def sneakerpedia_links(self,customPages): #custom pages are the SEARCH pages
        base = "http://www.sneakerpedia.com/search/sneaker_search?_=1490493921952&amp;keywords=&amp;page=4&amp;sort=1+&amp;sort_data[direction]=desc&amp;sort_data[field]=loves_count&amp;sort_data[title]=Most+loved&amp;utf8=&amp;year_from=&amp;year_to="
        r = requests.get(base).text
        soup = BeautifulSoup(r)
        shoeLinks = (
            ["http://www.sneakerpedia.com" + dict(ele.attrs).get('href')
             for ele in soup.find_all('a', attrs={'class':'hoverimage'})])
        for pageNumber in range(2,5):
            print(pageNumber)
            req = ("http://www.sneakerpedia.com/search/"
                   "sneaker_search?_=1490493921952&amp;"
                   "keywords=&amp;page={}&amp;"
                   "sort=1+&amp;"
                   "sort_data[direction]=desc&amp;"
                   "sort_data[field]=loves_count&amp;"
                   "sort_data[title]=Most+loved&amp;"
                   "utf8=&amp;year_from=&amp;year_to=").format(
                pageNumber
            )
            r = requests.get(req).text
            soup = BeautifulSoup(r)
            shoeLinks += (
                ["http://www.sneakerpedia.com" + dict(ele.attrs).get('href')
                 for ele in soup.find_all('a', attrs={'class': 'hoverimage'})])
        for link in customPages:
            r = requests.get(link).text
            soup = BeautifulSoup(r)
            shoeLinks += (
                ["http://www.sneakerpedia.com" + dict(ele.attrs).get('href')
                 for ele in soup.find_all('a', attrs={'class': 'hoverimage'})])
        print(len(list(set(shoeLinks))))
        print(list(set(shoeLinks)))
        return list(set(shoeLinks))

    def sneakerpedia(self,shoeLinks):
        base = "http://www.sneakerpedia.com/sneakers/"
        curr = 0
        shoeDictionary = {} # {shoe1:[1,2,3],shoe2:[4],...} shoe1 is name of shoe, value is list of picture names
        lenCurr = len(shoeLinks)
        dropped = 0
        failedResize = 0
        totalPics = 0
        for shoeLink in shoeLinks:
            curr += 1
            print("{}/{}".format(curr,lenCurr))
            r = requests.get(shoeLink).text
            soup = BeautifulSoup(r)
            try:
                name = soup.findAll('h2',class_='eip_label sneaker_name')[0].text
                brand = soup.findAll('p',class_="eip_label brand_name")[0].text
            except:
                print("Shoe Failed")
                dropped += 1
                continue
            print(name,brand)
            pics = [dict(ele.attrs).get('src','') for ele in soup.findAll('img',class_='carousel_thumb')]
            shoeDictionary[self.ff(name)] = brand
            for picUrl in pics:
                totalPics += 1
                picName = self.ff(name) + "QQQ" + picUrl.split('/')[-1].split('?')[0]
                r = requests.get(picUrl)
                with open(os.path.join(picDir, picName),'wb') as file:
                    file.write(r.content)
                    file.close()
                with open(os.path.join(picDir,picName), 'r+b') as f:
                    with Image.open(f) as image:
                        try:
                            cover = resizeimage.resize_cover(image, [155, 110])
                        except:
                            image.close()
                            f.close()
                            os.remove(os.path.join(picDir, picName)) # if we can't resize, we'll remove this pic.
                            print("shoe resize failure: deleteing picture.")
                            failedResize += 1
                cover.save(os.path.join(picDir,picName), image.format)
            time.sleep(1)
        print("Dropped {}/{} shoes".format(dropped,lenCurr))
        print("Dropped {}/{} pictures".format(failedResize, totalPics))
        return shoeDictionary

    # gets additional pictures from bing to suppliment ones we already have
    def getBingPicLinks(self):
        files = [os.path.basename(f)
                 for f in os.listdir(picDir) if os.path.isfile(os.path.join(picDir, f))]
        shoeNames = [str(ele).split('QQQ')[0] for ele in files]
        # before running a search, MAKE IT INTERNET (url) SAFE!
        base = "http://www.bing.com/images/search?q="
        for shoe in shoeNames: # these are already safe, we got theme strait from the file names
            time.sleep(1)
            query = base + shoe.replace(' ', '+')
            print(query)
            driver = webdriver.Chrome()
            driver.get(query)
            searchPage = driver.page_source
            soup = BeautifulSoup(searchPage)
            ImageLinks = [dict(ele.attrs).get('src') for ele in soup.find_all('img',{'class':'mimg'})]
            for picUrl in ImageLinks[:15]:
                if not picUrl:
                    print("not-a-url")
                    continue
                picName = self.ff(shoe) + "QQQ" + str(random.randint(1000000,20000000))
                print(picUrl)
                r = requests.get('http://bing.com/' + picUrl)
                with open(os.path.join(picDir , picName) + '.jpg','wb') as file:
                    file.write(r.content)
                    file.close()
                    try:
                       with open(os.path.join(picDir, picName), 'r+b') as f:
                           with Image.open(f) as image:
                               pass
                    except:
                        print("failed to load recourse: not a jpeg.")
                        continue
                with open(os.path.join(picDir , picName), 'r+b') as f:
                    with Image.open(f) as image:
                        try:
                            cover = resizeimage.resize_cover(image, [155, 110])
                        except:
                            image.close()
                            f.close()
                            os.remove(os.path.join(picDir, picName)) # if we can't resize, we'll remove this pic.
                            print("shoe resize failure: deleteing picture.")
                cover.save(os.path.join(picDir,picName), image.format)
            print(ImageLinks[0])


    # makes name usable as a file name
    def ff(self,value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """

        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = str(re.sub('[-\s]+', '-', value))
        return value

    def imgNametoPicNumber(self):
        # takes all files in the picDir, and creates a dictionary of pictures to shoe ({'shoe1':[1,2,3,4],...,})
        picdict = {}
        reversePicDict = {}
        files = [os.path.basename(f)
                 for f in os.listdir(picDir) if os.path.isfile(os.path.join(picDir, f))]
        count = 0
        for filename in files:
            filenameCommon = os.path.basename(filename)
            if filename in picdict.keys():
                picdict[filenameCommon].append(count)
            reversePicDict[filename] = count
        return picdict,reversePicDict



    def jpgToCsv(self):
        # takes all files in the picDir, and converts them into CSV
        picdict, reversePicDict = self.imgNametoPicNumber()
        try:
            os.mkdir(os.path.join(picDir,'CSV'))
        except:
            pass
        csvDir = os.path.join(picDir,'CSV')
        files = [f for f in os.listdir(picDir) if os.path.isfile(os.path.join(picDir, f))]
        rows = []
        numberOfFiles = len(files)
        curr = 0
        for file in files:
            curr += 1
            file = os.path.join(picDir,file)
            thisFilesNumber = reversePicDict[os.path.basename(file)]
            row = []
            print("file {} out of {}".format(curr, numberOfFiles))
            with Image.open(file) as file_to_read:
                pix = file_to_read.load()
                width, height = file_to_read.size
                filename = '.'.join(os.path.basename(file).split('.')[:-1]) + '.csv'
                for x in range(width):
                    for y in range(height):
                        r = pix[x,y][0]
                        g = pix[x,y][1]
                        b = pix[x,y][2]
                        value = str(int(r * 299.0 / 1000 + g * 587.0 / 1000 + b * 114.0 / 1000))
                        row.append(value)
            row.append(str(thisFilesNumber))
            rows.append(row)
        with open(os.path.join(csvDir, 'training.csv'),'w+') as file_to_write:
            print(len([str(ele) for ele in range(155*55)])+1)
            file_to_write.write(','.join([str(ele) for ele in range(155*55 + 1)])+ ',Label' + '\n')
            for row in rows:
                odd = False
                rowToWrite = ''
                for entry in row:
                    if not odd:
                        rowToWrite = rowToWrite + "," + entry
                        odd = True
                    else:
                        odd = False
                print(len(rowToWrite.split(',')))
                file_to_write.write(rowToWrite + '\n')

c = scrape()
# links = c.sneakerpedia_links(["http://www.sneakerpedia.com/search/sneakers?utf8=%E2%9C%93&keywords=NMD&commit=search",
#                       "http://www.sneakerpedia.com/search/sneakers?utf8=%E2%9C%93&keywords=Ultra+Boost&commit=search",
#                       "http://www.sneakerpedia.com/search/sneakers?utf8=%E2%9C%93&keywords=Roshe&commit=search"
#                       ])
links1 = ['http://www.sneakerpedia.com/sneakers/30298', 'http://www.sneakerpedia.com/sneakers/5145', 'http://www.sneakerpedia.com/sneakers/7068', 'http://www.sneakerpedia.com/sneakers/30465', 'http://www.sneakerpedia.com/sneakers/30303', 'http://www.sneakerpedia.com/sneakers/30488', 'http://www.sneakerpedia.com/sneakers/29623', 'http://www.sneakerpedia.com/sneakers/29511', 'http://www.sneakerpedia.com/sneakers/5', 'http://www.sneakerpedia.com/sneakers/5839', 'http://www.sneakerpedia.com/sneakers/28164', 'http://www.sneakerpedia.com/sneakers/1399', 'http://www.sneakerpedia.com/sneakers/2749', 'http://www.sneakerpedia.com/sneakers/3847', 'http://www.sneakerpedia.com/sneakers/29936', 'http://www.sneakerpedia.com/sneakers/24', 'http://www.sneakerpedia.com/sneakers/382', 'http://www.sneakerpedia.com/sneakers/30486', 'http://www.sneakerpedia.com/sneakers/29625', 'http://www.sneakerpedia.com/sneakers/28916', 'http://www.sneakerpedia.com/sneakers/737', 'http://www.sneakerpedia.com/sneakers/9352', 'http://www.sneakerpedia.com/sneakers/3839', 'http://www.sneakerpedia.com/sneakers/30254', 'http://www.sneakerpedia.com/sneakers/67', 'http://www.sneakerpedia.com/sneakers/774', 'http://www.sneakerpedia.com/sneakers/30300', 'http://www.sneakerpedia.com/sneakers/30032', 'http://www.sneakerpedia.com/sneakers/1546', 'http://www.sneakerpedia.com/sneakers/2310', 'http://www.sneakerpedia.com/sneakers/30073', 'http://www.sneakerpedia.com/sneakers/29607', 'http://www.sneakerpedia.com/sneakers/29616', 'http://www.sneakerpedia.com/sneakers/772', 'http://www.sneakerpedia.com/sneakers/1551', 'http://www.sneakerpedia.com/sneakers/21', 'http://www.sneakerpedia.com/sneakers/30219', 'http://www.sneakerpedia.com/sneakers/30051', 'http://www.sneakerpedia.com/sneakers/30393', 'http://www.sneakerpedia.com/sneakers/4631', 'http://www.sneakerpedia.com/sneakers/7158', 'http://www.sneakerpedia.com/sneakers/30345', 'http://www.sneakerpedia.com/sneakers/30487', 'http://www.sneakerpedia.com/sneakers/29927', 'http://www.sneakerpedia.com/sneakers/30338', 'http://www.sneakerpedia.com/sneakers/30352', 'http://www.sneakerpedia.com/sneakers/29838', 'http://www.sneakerpedia.com/sneakers/969', 'http://www.sneakerpedia.com/sneakers/29040', 'http://www.sneakerpedia.com/sneakers/30464', 'http://www.sneakerpedia.com/sneakers/28392', 'http://www.sneakerpedia.com/sneakers/756', 'http://www.sneakerpedia.com/sneakers/1003', 'http://www.sneakerpedia.com/sneakers/4889', 'http://www.sneakerpedia.com/sneakers/2321', 'http://www.sneakerpedia.com/sneakers/30380', 'http://www.sneakerpedia.com/sneakers/30269', 'http://www.sneakerpedia.com/sneakers/28173', 'http://www.sneakerpedia.com/sneakers/7501', 'http://www.sneakerpedia.com/sneakers/30302', 'http://www.sneakerpedia.com/sneakers/148', 'http://www.sneakerpedia.com/sneakers/681', 'http://www.sneakerpedia.com/sneakers/28454', 'http://www.sneakerpedia.com/sneakers/30457', 'http://www.sneakerpedia.com/sneakers/29787', 'http://www.sneakerpedia.com/sneakers/4002', 'http://www.sneakerpedia.com/sneakers/1075', 'http://www.sneakerpedia.com/sneakers/30456', 'http://www.sneakerpedia.com/sneakers/28945', 'http://www.sneakerpedia.com/sneakers/86', 'http://www.sneakerpedia.com/sneakers/2335', 'http://www.sneakerpedia.com/sneakers/28700', 'http://www.sneakerpedia.com/sneakers/29923', 'http://www.sneakerpedia.com/sneakers/3831', 'http://www.sneakerpedia.com/sneakers/29902', 'http://www.sneakerpedia.com/sneakers/30299', 'http://www.sneakerpedia.com/sneakers/28219', 'http://www.sneakerpedia.com/sneakers/596', 'http://www.sneakerpedia.com/sneakers/4877', 'http://www.sneakerpedia.com/sneakers/28526', 'http://www.sneakerpedia.com/sneakers/30460', 'http://www.sneakerpedia.com/sneakers/113', 'http://www.sneakerpedia.com/sneakers/29691', 'http://www.sneakerpedia.com/sneakers/30358', 'http://www.sneakerpedia.com/sneakers/2016', 'http://www.sneakerpedia.com/sneakers/825', 'http://www.sneakerpedia.com/sneakers/28108', 'http://www.sneakerpedia.com/sneakers/651', 'http://www.sneakerpedia.com/sneakers/6652', 'http://www.sneakerpedia.com/sneakers/1547', 'http://www.sneakerpedia.com/sneakers/28734', 'http://www.sneakerpedia.com/sneakers/29605', 'http://www.sneakerpedia.com/sneakers/1434', 'http://www.sneakerpedia.com/sneakers/1991', 'http://www.sneakerpedia.com/sneakers/49', 'http://www.sneakerpedia.com/sneakers/30427', 'http://www.sneakerpedia.com/sneakers/15927', 'http://www.sneakerpedia.com/sneakers/212', 'http://www.sneakerpedia.com/sneakers/5125', 'http://www.sneakerpedia.com/sneakers/1548', 'http://www.sneakerpedia.com/sneakers/3564', 'http://www.sneakerpedia.com/sneakers/758', 'http://www.sneakerpedia.com/sneakers/28803', 'http://www.sneakerpedia.com/sneakers/30283', 'http://www.sneakerpedia.com/sneakers/274', 'http://www.sneakerpedia.com/sneakers/572', 'http://www.sneakerpedia.com/sneakers/1510', 'http://www.sneakerpedia.com/sneakers/5302', 'http://www.sneakerpedia.com/sneakers/29606', 'http://www.sneakerpedia.com/sneakers/29248', 'http://www.sneakerpedia.com/sneakers/58', 'http://www.sneakerpedia.com/sneakers/2977', 'http://www.sneakerpedia.com/sneakers/2613', 'http://www.sneakerpedia.com/sneakers/30304', 'http://www.sneakerpedia.com/sneakers/30426', 'http://www.sneakerpedia.com/sneakers/4440', 'http://www.sneakerpedia.com/sneakers/28228', 'http://www.sneakerpedia.com/sneakers/1004', 'http://www.sneakerpedia.com/sneakers/701', 'http://www.sneakerpedia.com/sneakers/30010', 'http://www.sneakerpedia.com/sneakers/4879', 'http://www.sneakerpedia.com/sneakers/30271', 'http://www.sneakerpedia.com/sneakers/28910', 'http://www.sneakerpedia.com/sneakers/6507', 'http://www.sneakerpedia.com/sneakers/6026', 'http://www.sneakerpedia.com/sneakers/28107', 'http://www.sneakerpedia.com/sneakers/1358', 'http://www.sneakerpedia.com/sneakers/913', 'http://www.sneakerpedia.com/sneakers/30045', 'http://www.sneakerpedia.com/sneakers/72', 'http://www.sneakerpedia.com/sneakers/122', 'http://www.sneakerpedia.com/sneakers/764', 'http://www.sneakerpedia.com/sneakers/444', 'http://www.sneakerpedia.com/sneakers/28740', 'http://www.sneakerpedia.com/sneakers/776', 'http://www.sneakerpedia.com/sneakers/210', 'http://www.sneakerpedia.com/sneakers/12', 'http://www.sneakerpedia.com/sneakers/1000', 'http://www.sneakerpedia.com/sneakers/29945', 'http://www.sneakerpedia.com/sneakers/30381', 'http://www.sneakerpedia.com/sneakers/28396', 'http://www.sneakerpedia.com/sneakers/5074', 'http://www.sneakerpedia.com/sneakers/2691', 'http://www.sneakerpedia.com/sneakers/177', 'http://www.sneakerpedia.com/sneakers/905', 'http://www.sneakerpedia.com/sneakers/152', 'http://www.sneakerpedia.com/sneakers/920', 'http://www.sneakerpedia.com/sneakers/2308', 'http://www.sneakerpedia.com/sneakers/30485', 'http://www.sneakerpedia.com/sneakers/377', 'http://www.sneakerpedia.com/sneakers/1320', 'http://www.sneakerpedia.com/sneakers/28227', 'http://www.sneakerpedia.com/sneakers/2938', 'http://www.sneakerpedia.com/sneakers/755', 'http://www.sneakerpedia.com/sneakers/740', 'http://www.sneakerpedia.com/sneakers/29939', 'http://www.sneakerpedia.com/sneakers/2028', 'http://www.sneakerpedia.com/sneakers/3256', 'http://www.sneakerpedia.com/sneakers/26', 'http://www.sneakerpedia.com/sneakers/29', 'http://www.sneakerpedia.com/sneakers/498', 'http://www.sneakerpedia.com/sneakers/4580', 'http://www.sneakerpedia.com/sneakers/4475', 'http://www.sneakerpedia.com/sneakers/2914', 'http://www.sneakerpedia.com/sneakers/626', 'http://www.sneakerpedia.com/sneakers/4308']

c.jpgToCsv()



