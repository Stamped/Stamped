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
#import "STSynchronousWrapper.h"
#import "STGalleryViewFactory.h"

@interface STEntityDetailViewFactory()

@property (nonatomic, retain) NSString* style;

@end

@interface STEntityDetailViewFactoryOperation : NSOperation

- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail style:(NSString*)style andCallbackBlock:(STViewCreatorCallback)aBlock;

@property (nonatomic, readonly) NSMutableDictionary* operations;
@property (nonatomic, readonly) NSMutableDictionary* components;
@property (nonatomic, readonly) id<STEntityDetail> entityDetail;
@property (nonatomic, readwrite, copy) STViewCreatorCallback callback;

@end

@implementation STEntityDetailViewFactoryOperation

@synthesize operations = operations_;
@synthesize components = components_;
@synthesize entityDetail = entityDetail_;
@synthesize callback = callback_;

- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail style:(NSString*)style andCallbackBlock:(STViewCreatorCallback)aBlock;
{
  self = [super init];
  if (self) {
    entityDetail_ = [anEntityDetail retain];
    self.callback = aBlock;
    operations_ = [[NSMutableDictionary alloc] init];
    components_ = [[NSMutableDictionary alloc] init];
    NSArray* components;
    if ([style isEqualToString:@"StampDetail"]) {
      components = [NSArray arrayWithObjects:
                    @"actions",
                    nil];
    }
    else {
      components = [NSArray arrayWithObjects:
                    @"header",
                    @"actions",
                    @"metadata",
                    nil];
    }
    for (id k in components) {
      [self.operations setObject:[[[NSOperation alloc] init] autorelease] forKey:k];
    }
  }
  return self;
}

- (void)dealloc
{
  [operations_ release];
  [components_ release];
  [entityDetail_ release];
  self.callback = nil;
  [super dealloc];
}

- (void)cancel {
  for (id operation in [self.operations allValues]) {
    [operation cancel];
  }
  [super cancel];
}

- (UIView*)createViewWithDelegate:(id<STViewDelegate>)delegate {
  STViewContainer* view = [[[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 0)] autorelease];
  NSArray* keys = [NSArray arrayWithObjects:@"header", @"actions", @"metadata", nil];
  for (NSString* key in keys) {
    @synchronized(self.components) {
      STViewCreator creator = [self.components objectForKey:key];
      if (creator)
      {
        UIView* child = creator(view);
        if (child)
        {
          [view appendChildView:child];
        }
      }
    }
  }
  id<STEntityDetailComponentFactory> factory = [[[STGalleryViewFactory alloc] init] autorelease];
  UIView* wrapper = [[STSynchronousWrapper alloc] initWithDelegate:view componentFactory:factory 
                                                      entityDetail:self.entityDetail 
                                                          andFrame:CGRectMake(0, 0, 320, 200)];
  [view appendChildView:wrapper];
  return view;
}

- (void)main {
  NSOperationQueue* queue = [[[NSOperationQueue alloc] init] autorelease];
  for (NSString* key in [self.operations allKeys]) {
    NSOperation* operation = [self.operations objectForKey:key];
    id<STEntityDetailComponentFactory> factory = nil;
    if ([key isEqualToString:@"header"]) {
      factory = [[[STHeaderViewFactory alloc] init] autorelease];
    }
    else if ([key isEqualToString:@"actions"]) {
      factory = [[[STActionsViewFactory alloc] init] autorelease];
    }
    else if ([key isEqualToString:@"metadata"]) {
      factory = [[[STMetadataViewFactory alloc] init] autorelease];
    }
    NSOperation* op = [factory createViewWithEntityDetail:self.entityDetail andCallbackBlock:^(STViewCreator creator) {
      @synchronized(self.components) {
        STViewCreator copy = [[creator copy] autorelease];
        [self.components setObject:copy forKey:key];
        [operation start];
      }
    }];
    [queue addOperation:op];
  }
  for (NSOperation* operation in [self.operations allValues]) {
    [operation waitUntilFinished];
  }
  dispatch_async(dispatch_get_main_queue(), ^{
    @autoreleasepool {
      STViewCreator creator = ^(id<STViewDelegate> delegate) {
        return [self createViewWithDelegate:delegate];
      };
      self.callback(creator);
    }
  });
}


@end

@implementation STEntityDetailViewFactory

@synthesize style = style_;

- (id)initWithStyle:(NSString*)style {
  self = [super init];
  if (self) {
    self.style = style;
  }
  return self;
}

- (id)init {
  self = [super init];
  if (self) {
    self.style = @"EntityDetail";
  }
  return self;
}

- (NSOperation*)createViewWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock {
  STEntityDetailViewFactoryOperation* operation = [[[STEntityDetailViewFactoryOperation alloc] initWithEntityDetail:anEntityDetail style:self.style andCallbackBlock:aBlock] autorelease];
  return operation;
}

@end
