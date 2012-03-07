//
//  STSimpleEntityDetail.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntityDetail.h"
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
   @"title",@"title",
   nil];
  [mapping mapAttributes:
   @"desc",
   nil];
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
}

#pragma mark - Private Methods.

- (void)loadDataFromServer:(NSString*)entityID {
  loading_ = TRUE;
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    return;
  } 
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [RKO
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:self];
  
  objectLoader.objectMapping = mapping;
  
  NSString* key = @"entity_id";
  NSLog(@"testing string");
  objectLoader.params = [NSDictionary dictionaryWithObject:entityID forKey:key];
  
  [objectLoader send];
}

@end
