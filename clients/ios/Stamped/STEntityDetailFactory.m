//
//  STEntityDetailFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityDetailFactory.h"
#import <RestKit/RestKit.h>
#import "STSimpleEntityDetail.h"

static NSString* const kEntityLookupPath = @"/entities/show.json";

@interface STEntityDetailFactoryHelper : NSObject <RKObjectLoaderDelegate>

@property (nonatomic, retain) id<STFactoryDelegate> delegate;
@property (nonatomic, retain) id label;

@end

@implementation STEntityDetailFactoryHelper

@synthesize delegate = delegate_;
@synthesize label = label_;

#pragma mark - RKObjectLoaderDelegate Methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [self.delegate didLoad:nil withLabel:self.label];
  [self autorelease];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  STSimpleEntityDetail* detail = [objects objectAtIndex:0];
  NSLog(@"This is %@ with desc:\n%@", detail.title, detail.desc);
  if (detail.gallery) {
    for (id<STGalleryItem> item in detail.gallery.data) {
      NSLog(@"image %@",item.image);
    }
  }
  [self.delegate didLoad:detail withLabel:self.label];
  [self autorelease];
}

@end

@implementation STEntityDetailFactory

#pragma mark - Public Methods.

- (void)createWithEntityId:(NSString*)entityID delegate:(id<STFactoryDelegate>)delegate label:(id)label {
  if (entityID == nil) {
    [delegate didLoad:nil withLabel:label];
    return;
  }
  RKClient* client = [RKClient sharedClient];
  if (client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable) {
    [delegate didLoad:nil withLabel:label];
    return;
  }
  
  STEntityDetailFactoryHelper* helper = [[STEntityDetailFactoryHelper alloc] init];
  helper.delegate = delegate;
  helper.label = label;
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:helper];
  
  objectLoader.objectMapping = [STSimpleEntityDetail mapping];
  
  NSString* key = @"entity_id";
  objectLoader.params = [NSDictionary dictionaryWithObject:entityID forKey:key];
  
  [objectLoader send];
}

@end
