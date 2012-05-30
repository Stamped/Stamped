//
//  STSimpleEntityDetail.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "STSimpleEntity.h"
#import <RestKit/RestKit.h>

@interface STSimpleEntityDetail : STSimpleEntity <STEntityDetail>

@property (nonatomic, readwrite, retain) NSString* caption;

@property (nonatomic, readwrite, retain) NSString* address;
@property (nonatomic, readwrite, retain) NSString* addressStreet;
@property (nonatomic, readwrite, retain) NSString* addressCity;
@property (nonatomic, readwrite, retain) NSString* addressState;
@property (nonatomic, readwrite, retain) NSString* addressZip;
@property (nonatomic, readwrite, retain) NSString* addressCountry;
@property (nonatomic, readwrite, retain) NSString* neighborhood;

@property (nonatomic, readwrite, retain) NSArray<STActionItem>* actions;
@property (nonatomic, readwrite, retain) NSArray<STMetadataItem>* metadata;
@property (nonatomic, readwrite, retain) NSArray<STGallery>* galleries;
@property (nonatomic, readwrite, retain) id<STPlaylist> playlist;
@property (nonatomic, readwrite, retain) id<STPreviews> previews;

+ (RKObjectMapping*)mapping;

@end
