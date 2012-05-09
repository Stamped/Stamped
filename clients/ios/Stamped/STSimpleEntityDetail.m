//
//  STSimpleEntityDetail.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntityDetail.h"
#import "STSimpleActionItem.h"
#import "STSimpleMetadataItem.h"
#import "STSimpleGallery.h"
#import "STSimplePlaylist.h"
#import <RestKit/RestKit.h>
#import "STSimpleImageList.h"

#pragma mark - Attributes

@implementation STSimpleEntityDetail

@synthesize caption = _caption;

@synthesize address = _address;
@synthesize addressStreet = _addressStreet;
@synthesize addressCity = _addressCity;
@synthesize addressState = _addressState;
@synthesize addressZip = _addressZip;
@synthesize addressCountry = _addressCountry;
@synthesize neighborhood = _neighborhood;

@synthesize actions = _actions;
@synthesize metadata = _metadata;
@synthesize galleries = _galleries;
@synthesize playlist = _playlist;

- (void)dealloc {
  [_caption release];
  
  [_address release];
  [_addressStreet release];
  [_addressCity release];
  [_addressState release];
  [_addressZip release];
  [_addressCountry release];
  [_neighborhood release];
  
  [_actions release];
  [_metadata release];
  [_galleries release];
  [_playlist release];
  
  [super dealloc];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntityDetail class]];
  
  [mapping mapKeyPathsToAttributes:
   @"entity_id", @"entityID",
   @"address_street", @"addressStreet",
   @"address_city", @"addressCity",
   @"address_state", @"addressState",
   @"address_zip", @"addressZip",
   @"address_country", @"addressCountry",
   nil];
  
  [mapping mapAttributes:
   @"title",
   @"subtitle",
   @"category",
   @"subcategory",
   @"coordinates",
   @"address",
   @"neighborhood",
   @"caption",
   nil];
  
  [mapping mapRelationship:@"images" withMapping:[STSimpleImageList mapping]];
  [mapping mapRelationship:@"actions" withMapping:[STSimpleActionItem mapping]];
  [mapping mapRelationship:@"metadata" withMapping:[STSimpleMetadataItem mapping]];
  [mapping mapRelationship:@"galleries" withMapping:[STSimpleGallery mapping]];
  [mapping mapRelationship:@"playlist" withMapping:[STSimplePlaylist mapping]];
  return mapping;
}


@end
