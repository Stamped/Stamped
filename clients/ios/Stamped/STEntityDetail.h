//
//  STEntityDetail.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STAction;
@protocol STGallery;
@protocol STMetadata;
@protocol STPlaylist;
@protocol STFriends;
@protocol STRelated;

@protocol STEntityDetail <NSObject>

@property (nonatomic, readonly, retain) NSString* entityID;
@property (nonatomic, readonly, retain) NSString* title;
@property (nonatomic, readonly, retain) NSString* subtitle;
@property (nonatomic, readonly, retain) NSString* desc;
@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* subcategory;
@property (nonatomic, readonly, retain) NSString* image;

@property (nonatomic, readonly, retain) NSString* address;
@property (nonatomic, readonly, retain) NSString* addressStreet;
@property (nonatomic, readonly, retain) NSString* addressCity;
@property (nonatomic, readonly, retain) NSString* addressState;
@property (nonatomic, readonly, retain) NSString* addressZip;
@property (nonatomic, readonly, retain) NSString* addressCountry;
@property (nonatomic, readonly, retain) NSString* neighborhood;
@property (nonatomic, readonly, retain) NSString* coordinates;

@property (nonatomic, readonly, retain) NSArray<STAction>* actions;
@property (nonatomic, readonly, retain) id<STMetadata> metadata;
@property (nonatomic, readonly, retain) id<STGallery> gallery;
@property (nonatomic, readonly, retain) id<STPlaylist> playlist;

@end
