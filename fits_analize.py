__author__ = 'pablogsal'


import os
import fnmatch
import pyfits as fits
import argparse
import utilities
import time
import numpy as np
import tabulate




parser = argparse.ArgumentParser(description='Analize fits images.')

parser.add_argument('dir', metavar='dir', type=str, nargs=1,
                   help='The work directory containing the images.')
parser.add_argument('--verbose', dest='verbose_flag', action='store_const',
                   const=True, default=False,
                   help='Prints more info (default: False)')
parser.add_argument('--r_night', dest='night_flag', action='store_const',
                   const=True, default=False,
                   help='Remove the night if the night has been detectes as outlier in general (default: False)')
parser.add_argument('--r_internight', dest='internight_flag', action='store_const',
                   const=True, default=False,
                   help=' Remove the INTER-outliers if the night has been detectes as outlier in general(default: '
                        'False)')
parser.add_argument('--r_out', dest='out_flag', action='store_const',
                   const=True, default=False,
                   help='Remove all outlayers (default: False)')
parser.add_argument('--r_bad-nights', dest='badnights_flag', action='store_const',
                   const=True, default=False,
                   help='Remove all nights with less than 3 objects (default: False)')
parser.add_argument('--r_cloud_mea', dest='clouds_flag', action='store_const',
                   const=True, default=False,
                   help='Remove images with clouds using average values(default: False)')
parser.add_argument('--r_cloud_std', dest='clouds_sigma_flag', action='store_const',
                   const=True, default=False,
                   help='Remove images with clouds using sigma values(default: False)')
parser.add_argument('--nodata', dest='data_flag', action='store_const',
                   const=False, default=True,
                   help='Do not remove data outlayers (default: False)')
parser.add_argument('--darks', dest='dark_flag', action='store_const',
                   const=True, default=False,
                   help='Remove dark outlayers (default: False)')
parser.add_argument('--flats', dest='flat_flag', action='store_const',
                   const=True, default=False,
                   help='Remove flat outlayers (default: False)')


args = parser.parse_args()

work_dir=args.dir[0]





#FUNCTIONS
###############################################################

#This deletes the INTER-outliers if the night has been detectes as outlier in general


def remove_internight(clean_list):
    global deleteflag
    print(utilities.bcolors.WARNING+'I will remove inter-outlier for outlier nights'+utilities.bcolors.ENDC+'\n')


    outliers_list_pos=utilities.find_outlayers(utilities.night_stats(clean_list).median())
    for i in outliers_list_pos:
        temp=utilities.find_outlayers([a.average for a in clean_list[i]] )
        blacklist= [clean_list[i][j].direction for j in temp ]

        for blackitem in blacklist:
            os.remove(blackitem)
            print("Removed "+blackitem)



#This deletes the INTER-outliers for all nights

def remove_interall(clean_list):
    global deleteflag
    print(utilities.bcolors.FAIL+'I will remove inter-outlier for all nights'+utilities.bcolors.ENDC+'\n')

    for i in range(len(clean_list)):
        temp=utilities.find_outlayers([a.average for a in clean_list[i]] )
        blacklist= [clean_list[i][j].direction for j in temp  ]

        for blackitem in blacklist:
            os.remove(blackitem)
            print("Removed "+blackitem)



#This deletes the night if the night has been detectes as outlier in general

def remove_night(clean_list):
    global deleteflag
    print(utilities.bcolors.FAIL+'I will remove outlier nights'+utilities.bcolors.ENDC+'\n')

    outliers_list_pos=utilities.find_outlayers(utilities.night_stats(clean_list).median())
    for i in outliers_list_pos:
        blacklist= [j.direction for j in clean_list[i]]

        for blackitem in blacklist:
            os.remove(blackitem)
            print("Removed "+blackitem)

#This deletes the night if the night has been detectes as bad in general


def remove_badnight(clean_list):
    print(utilities.bcolors.FAIL+'I will remove bad nights'+utilities.bcolors.ENDC+'\n')

    bad=[i for i in clean_list if len(i)<3 ]
    for night in bad:
        for bad_file in night:
            os.remove(bad_file.direction)
            print("Removed "+bad_file.direction)

    print('Removed '+str(len(bad))+' bad nights.')
    file.write('Removed '+str(len(bad))+' bad nights.')
    print('\n')
    file.write('\n' )


def remove_cludy(clean_list):
    print(utilities.bcolors.FAIL+'I will remove cloudy images'+utilities.bcolors.ENDC+'\n')
    filelist=[]
    for night in clean_list:
        for test_file in night:
            filelist.append(test_file)

    clouds=[]
    blacklist=[a for a in filelist if a.average >= 600 ]

    for bad_file in blacklist:
            os.remove(bad_file.direction)
            print("Removed "+bad_file.direction)
            clouds.append(["/".join(bad_file.give_time()[0:3]),bad_file.average])

    print('Removed '+str(len(blacklist))+' cloudy images.')
    file.write('\n' )
    file.write('Removed '+str(len(blacklist))+' cloudy images.')
    print('\n')
    if len(clouds)>0:
        file.write('\n' )
        file.write(tabulate.tabulate(clouds, headers=['Date', 'Medians'], tablefmt='orgtbl'))

    file.write('\n' )

def remove_cludy_std(clean_list):
    print(utilities.bcolors.FAIL+'I will remove cloudy images'+utilities.bcolors.ENDC+'\n')
    filelist=[]
    for night in clean_list:
        for test_file in night:
            filelist.append(test_file)

    clouds=[]
    blacklist=[a for a in filelist if a.stdev <= 7 ]

    for bad_file in blacklist:
            os.remove(bad_file.direction)
            print("Removed "+bad_file.direction)
            clouds.append(["/".join(bad_file.give_time()[0:3]),bad_file.stdev])

    print('Removed '+str(len(blacklist))+' cloudy images.')
    file.write('\n' )
    file.write('Removed '+str(len(blacklist))+' cloudy images.')
    print('\n')
    if len(clouds)>0:
        file.write('\n' )
        file.write(tabulate.tabulate(clouds, headers=['Date', 'Stdev'], tablefmt='orgtbl'))

    file.write('\n' )




##################################################################









#Construct a list of files

matches=[]
for root, dir, files in os.walk(work_dir):
    for items in fnmatch.filter(files, "*.fits"):
        matches.append(os.path.join(root, items))





#Construct file list

fits_list=[]
meantime=[]

print('\n'+utilities.bcolors.OKBLUE+'Constructing the data '
                                    'index:'+'\n'+'---------------------------------------'+utilities.bcolors.ENDC+'\n')

#Get the files

for i in matches:
    start = time.time()
    fits_list.append(  utilities.fits_image(i,
                             fits.getheader(i)["IMAGETYP"],
                             fits.getheader(i)["EXPTIME"],
                             fits.getheader(i)["FILTER"],
                             fits.getheader(i)["DATE-OBS"],
                             fits.getheader(i)["AVERAGE"],
                             fits.getheader(i)["STDEV"],
                             fits.getheader(i)["AIRMASS"],
                             fits.getheader(i)["OBJRA"],
                             fits.getheader(i)["OBJDEC"]
                             )   )
    end =time.time()
    meantime.append(end - start)
    utilities.update_progress(float(len(fits_list)) / len(matches), np.mean(meantime) * (len(matches)-len(
        fits_list)))


#Classify the files for dates

images=[i for i in fits_list if i.type=='object']
darks=[i for i in fits_list if i.type=='dark']
flats=[i for i in fits_list if i.type=='flat']



datadates=list(sorted(set(["".join(i.give_time()[0:3]) for i in images])))
darkdates=list(sorted(set(["".join(i.give_time()[0:3]) for i in darks])))
flatdates=list(sorted(set(["".join(i.give_time()[0:3]) for i in flats])))


image_classified=[]
for date_i in datadates:
    image_classified.append( [i for i in images if "".join(i.give_time()[0:3]) == date_i ])

dark_classified=[]
for date_i in darkdates:
    dark_classified.append( [i for i in darks if "".join(i.give_time()[0:3]) == date_i ])

flat_classified=[]
for date_i in flatdates:
    flat_classified.append( [i for i in flats if "".join(i.give_time()[0:3]) == date_i ])


#Calculate number of files


n_images=len(datadates)
n_darks=len(darkdates)
n_flats=len(flatdates)

print( 'I found '+str(n_images)+' images, '+str(n_darks)+' darks and '+str(n_flats)+' flats.'+'\n')

#Print data if verbose flag is active
if args.verbose_flag == True:
    print('\n'+utilities.bcolors.OKGREEN+'Found data:'+'\n')

printdata=[]

means=utilities.night_stats(image_classified).mean()
medians=utilities.night_stats(image_classified).median()
stdss=utilities.night_stats(image_classified).std()
mean_stdss=utilities.night_stats(image_classified).mean_std()




for i in range(len(datadates)):
    printdata.append([datadates[i],medians[i],means[i],stdss[i],mean_stdss[i], len(image_classified[i])]  )

if args.verbose_flag == True:
    print (tabulate.tabulate(printdata, headers=['Night', 'Medians','Means',"Std(means)","Mean std","#"],
                             tablefmt='orgtbl') )
    print ('\n'+"-----End data--------"+utilities.bcolors.ENDC+'\n')

file=open(work_dir+'/stats.txt', 'w')
file.write(tabulate.tabulate(printdata, headers=['Night', 'Medians','Means',"Std(means)","Mean std","#"],
                             tablefmt='orgtbl'))
file.write('\n'+'\n'+'\n'+'\n')



#Print the outlayers



utilities.print_outlayers(image_classified,"data",file)
utilities.print_outlayers(dark_classified,"darks",file)
utilities.print_outlayers(flat_classified,"flats",file)


#Kill outlayers if flags are active


if args.night_flag or args.internight_flag or args.out_flag:

    if args.night_flag:
        if args.data_flag:
            remove_night(image_classified)
        if args.dark_flag:
            remove_night(dark_classified)
        if args.flat_flag:
            remove_night(flat_classified)

    elif args.internight_flag:
        if args.data_flag:
            remove_internight(image_classified)
        if args.dark_flag:
            remove_internight(dark_classified)
        if args.flat_flag:
            remove_internight(flat_classified)

    elif args.out_flag:
        if args.data_flag:
            remove_interall(image_classified)
        if args.dark_flag:
            remove_interall(dark_classified)
        if args.flat_flag:
            remove_interall(flat_classified)

    else:
        print(utilities.bcolors.WARNING+'No files deleted'+utilities.bcolors.ENDC+'\n')

else:
    print(utilities.bcolors.WARNING+'No files deleted'+utilities.bcolors.ENDC+'\n')



#Statistics about the number of files

number_files=[]
for i in range(len(datadates)):
    number_files.append( len(image_classified[i])  )

file_mean=np.mean(number_files)
file_median=np.median(number_files)
file_std=np.std(number_files)


print('\n')
file.write('\n' )

print(tabulate.tabulate([[file_mean,file_median,file_std]], headers=['File mean', 'File median','File sigma'],\
                                                                   tablefmt='orgtbl') )
file.write(tabulate.tabulate([[file_mean,file_median,file_std]], headers=['File mean', 'File median','File sigma'],\
                                                                        tablefmt='orgtbl') )
print('\n')
file.write('\n' )


if len([i for i in image_classified if len(i)<3 ]) > len( image_classified )/2:
    print(utilities.bcolors.FAIL+'A LOT OF BAD NIGHTS!! - Consider cleaning those.  :('+utilities.bcolors.ENDC+'\n')

#Remove bad nights if flag is active

if args.badnights_flag:
    remove_badnight(image_classified)

if args.clouds_flag:
    remove_cludy(image_classified)

if args.clouds_sigma_flag:
    remove_cludy_std(image_classified)


file.close()


