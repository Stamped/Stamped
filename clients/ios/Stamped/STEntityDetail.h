//
//  STEntityDetail.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActionItem.h"
#import "STGallery.h"
#import "STMetadataItem.h"
#import "STPlaylist.h"
#import "STEntity.h"
#import "STImage.h"

@protocol STEntityDetail <STEntity>

@property (nonatomic, readonly, retain) NSString* caption;

@property (nonatomic, readonly, retain) NSString* address;
@property (nonatomic, readonly, retain) NSString* addressStreet;
@property (nonatomic, readonly, retain) NSString* addressCity;
@property (nonatomic, readonly, retain) NSString* addressState;
@property (nonatomic, readonly, retain) NSString* addressZip;
@property (nonatomic, readonly, retain) NSString* addressCountry;
@property (nonatomic, readonly, retain) NSString* neighborhood;

@property (nonatomic, readonly, retain) NSArray<STActionItem>* actions;
@property (nonatomic, readonly, retain) NSArray<STMetadataItem>* metadata;
@property (nonatomic, readonly, retain) NSArray<STGallery>* galleries;
@property (nonatomic, readonly, retain) id<STPlaylist> playlist;

@end
