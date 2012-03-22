//
//  STSimpleEntityDetail.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import <RestKit/RestKit.h>


@interface STSimpleEntityDetail : NSObject <STEntityDetail>

@property (nonatomic, readwrite, retain) NSString* entityID;
@property (nonatomic, readwrite, retain) NSString* title;
@property (nonatomic, readwrite, retain) NSString* subtitle;
@property (nonatomic, readwrite, retain) NSString* desc;
@property (nonatomic, readwrite, retain) NSString* category;
@property (nonatomic, readwrite, retain) NSString* subcategory;
@property (nonatomic, readwrite, retain) NSString* image;
@property (nonatomic, readwrite, retain) NSString* caption;

@property (nonatomic, readwrite, retain) NSString* address;
@property (nonatomic, readwrite, retain) NSString* addressStreet;
@property (nonatomic, readwrite, retain) NSString* addressCity;
@property (nonatomic, readwrite, retain) NSString* addressState;
@property (nonatomic, readwrite, retain) NSString* addressZip;
@property (nonatomic, readwrite, retain) NSString* addressCountry;
@property (nonatomic, readwrite, retain) NSString* neighborhood;
@property (nonatomic, readwrite, retain) NSString* coordinates;

@property (nonatomic, readwrite, retain) NSArray<STActionItem>* actions;
@property (nonatomic, readwrite, retain) NSArray<STMetadataItem>* metadata;
@property (nonatomic, readwrite, retain) id<STGallery> gallery;
@property (nonatomic, readwrite, retain) id<STPlaylist> playlist;

+ (RKObjectMapping*)mapping;

@end