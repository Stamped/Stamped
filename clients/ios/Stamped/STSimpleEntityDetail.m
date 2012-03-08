//
//  STSimpleEntityDetail.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntityDetail.h"
#import "STSimpleAction.h"
#import "STSimpleMetadata.h"
#import "STSimpleGallery.h"
#import "STSimplePlaylist.h"
#import "STGalleryItem.h"
#import <RestKit/RestKit.h>

static NSString* const kEntityLookupPath = @"/entities/show.json";

#pragma mark - Private Interface.

@interface STSimpleEntityDetail () 
- (void)loadDataFromServer:(NSString*)entityID;
@end

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

@synthesize loading = loading_;
@synthesize failed = failed_;

#pragma mark - Initialization.

- (id)initWithEntityId:(NSString*)entityID {
  self = [super init];
  if (self) {
    [self loadDataFromServer:entityID];
  }
  return self;
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
  [mapping mapRelationship:@"metadata" withMapping:[STSimpleMetadata mapping]];
  [mapping mapRelationship:@"gallery" withMapping:[STSimpleGalleryItem mapping]];
  [mapping mapRelationship:@"playlist" withMapping:[STSimplePlaylist mapping]];
  return mapping;
}

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  failed_ = YES;
  loading_ = NO;
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  STSimpleEntityDetail* detail = [objects objectAtIndex:0];
  NSLog(@"This is %@ with desc:\n%@", detail.title, detail.desc);
  if (detail.gallery) {
    NSArray* data = detail.gallery.data;
    if (data) {
      for (id<STGalleryItem> item in data) {
        NSLog(@"value %@",item.image);
      }
    }
  }
}

#pragma mark - Private Methods.

- (void)loadDataFromServer:(NSString*)entityID {
  loading_ = TRUE;
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    return;
  } 
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:self];
  
  objectLoader.objectMapping = [STSimpleEntityDetail mapping];
  
  NSString* key = @"entity_id";
  NSLog(@"testing string");
  objectLoader.params = [NSDictionary dictionaryWithObject:entityID forKey:key];
  
  [objectLoader send];
}

@end
