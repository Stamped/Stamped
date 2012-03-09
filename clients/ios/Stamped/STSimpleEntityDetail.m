//
//  STSimpleEntityDetail.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntityDetail.h"
#import "STSimpleAction.h"
#import "STSimpleMetadataItem.h"
#import "STSimpleGallery.h"
#import "STSimplePlaylist.h"
#import "STGalleryItem.h"
#import <RestKit/RestKit.h>

#pragma mark - Attributes

@implementation STSimpleEntityDetail

@synthesize entityID = entityID_;
@synthesize title = title_;
@synthesize subtitle = subtitle_;
@synthesize desc = desc_;
@synthesize category = category_;
@synthesize subcategory = subcategory_;
@synthesize image = image_;

@synthesize address = address_;
@synthesize addressStreet = addressStreet_;
@synthesize addressCity = addressCity_;
@synthesize addressState = addressState_;
@synthesize addressZip = addressZip_;
@synthesize addressCountry = addressCountry_;
@synthesize neighborhood = neighborhood_;
@synthesize coordinates = coordinates_;

@synthesize actions = actions_;
@synthesize metadata = metadata_;
@synthesize gallery = gallery_;
@synthesize playlist = playlist_;

- (void)dealloc {
  self.entityID = nil;
  self.title = nil;
  self.subtitle = nil;
  self.desc = nil;
  self.category = nil;
  self.subcategory = nil;
  self.image = nil;
  
  self.address = nil;
  self.addressStreet = nil;
  self.addressCity = nil;
  self.addressState = nil;
  self.addressZip = nil;
  self.addressCountry = nil;
  self.neighborhood = nil;
  self.coordinates = nil;
  
  self.actions = nil;
  self.metadata = nil;
  self.gallery = nil;
  self.playlist = nil;
  
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
   @"desc",
   @"category",
   @"subcategory",
   @"image",
   @"address",
   @"neighborhood",
   @"coordinates",
   nil];
  [mapping mapRelationship:@"actions" withMapping:[STSimpleAction mapping]];
  [mapping mapRelationship:@"metadata" withMapping:[STSimpleMetadataItem mapping]];
  [mapping mapRelationship:@"gallery" withMapping:[STSimpleGallery mapping]];
  [mapping mapRelationship:@"playlist" withMapping:[STSimplePlaylist mapping]];
  return mapping;
}


@end
