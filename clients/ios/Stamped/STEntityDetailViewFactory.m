//
//  STEntityDetailViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityDetailViewFactory.h"
#import "Util.h"
#import "STViewContainer.h"
#import "STViewDelegate.h"
#import "STEntityDetailComponentFactory.h"
#import "STHeaderViewFactory.h"
#import "STActionsViewFactory.h"
#import "STMetadataViewFactory.h"

@interface STEntityDetailViewFactoryOperation : NSOperation

- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock;

@property (nonatomic, readonly) NSMutableDictionary* operations;
@property (nonatomic, readonly) NSMutableDictionary* components;
@property (nonatomic, readonly) id<STEntityDetail> entityDetail;
@property (nonatomic, readonly) STViewCreatorCallback callback;

@end

@implementation STEntityDetailViewFactoryOperation

@synthesize operations = operations_;
@synthesize components = components_;
@synthesize entityDetail = entityDetail_;
@synthesize callback = callback_;

- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock;
{
  self = [super init];
  if (self) {
    entityDetail_ = [anEntityDetail retain];
    callback_ = [aBlock retain];
    operations_ = [NSMutableDictionary dictionary];
    components_ = [NSMutableDictionary dictionary];
    NSArray* components = [NSArray arrayWithObjects:
                           @"header",
                           @"actions",
                           @"metadata",
                           nil];
    for (id k in components) {
      [self.operations setObject:[[[NSOperation alloc] init] autorelease] forKey:k];
    }
  }
  return self;
}

- (void)dealloc
{
  [self.operations release];
  [self.components release];
  [self.entityDetail release];
  [self.callback release];
  [super dealloc];
}

- (void)cancel {
  for (id operation in [self.operations allValues]) {
    [operation cancel];
  }
  [super cancel];
}

- (void)main {
  for (NSString* key in [self.operations allKeys]) {
    NSOperation* operation = [self.operations objectForKey:key];
    STViewCreator creator = nil;
    id<STEntityDetailComponentFactory> factory = nil;
    if ([key isEqualToString:@"header"]) {
      creator = ^(id<STViewDelegate> delegate) {
        UIView* result = nil;
        [operation start];
        return result;
      };
      factory = [[[STHeaderViewFactory alloc] init] autorelease];
    }
    else if ([key isEqualToString:@"actions"]) {
      creator = ^(id<STViewDelegate> delegate) {
        UIView* result = nil;
        [operation start];
        return result;
      };
      factory = [[[STActionsViewFactory alloc] init] autorelease];
    }
    else if ([key isEqualToString:@"metadata"]) {
      creator = ^(id<STViewDelegate> delegate) {
        UIView* result = nil;
        [operation start];
        return result;
      };
      factory = [[[STMetadataViewFactory alloc] init] autorelease];
    }
    [factory createViewWithEntityDetail:self.entityDetail andCallbackBlock:nil];
  }
}


@end

@implementation STEntityDetailViewFactory

- (NSOperation*)createViewWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock {
  STEntityDetailViewFactoryOperation* operation = [[[STEntityDetailViewFactoryOperation alloc] initWithEntityDetail:anEntityDetail andCallbackBlock:aBlock] autorelease];
  return operation;
}

@end
