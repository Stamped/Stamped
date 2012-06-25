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
#import "STPlaylistViewFactory.h"
#import "STStampedAPI.h"
#import "STStampedByView.h"

@interface STEntityDetailViewFactory()

@property (nonatomic, readonly, retain) STActionContext* context;

@end

@interface STEntityDetailViewFactoryOperation : NSOperation

- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail context:(STActionContext*)context andCallbackBlock:(STViewCreatorCallback)aBlock;

@property (nonatomic, readonly, retain) STActionContext* context;
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
@synthesize context = _context;


- (id)initWithEntityDetail:(id<STEntityDetail>)anEntityDetail context:(STActionContext*)context andCallbackBlock:(STViewCreatorCallback)aBlock
{
    self = [super init];
    if (self) {
        _context = [context retain];
        entityDetail_ = [anEntityDetail retain];
        self.callback = aBlock;
        operations_ = [[NSMutableDictionary alloc] init];
        components_ = [[NSMutableDictionary alloc] init];
        NSArray* components;
        if (context.stamp) {
            components = [NSArray arrayWithObjects:
                          @"actions",
                          @"header",
                          //@"playlist",
                          nil];
        }
        else {
            components = [NSArray arrayWithObjects:
                          @"header",
                          @"actions",
                          @"metadata",
                          @"playlist",
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
    [_context release];
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
    BOOL loadedSomething = NO;
    STViewContainer* view = [[[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 0)] autorelease];
    NSArray* keys = [NSArray arrayWithObjects:@"header", @"actions", @"metadata", @"playlist", nil];
    if (self.context.stamp) {
        keys = [NSArray arrayWithObjects:@"actions", @"header", nil];
    }
    for (NSString* key in keys) {
        @synchronized(self.components) {
            STViewCreator creator = [self.components objectForKey:key];
            if (creator)
            {
                UIView* child = creator(view);
                if (child)
                {
                    [view appendChildView:child];
                    loadedSomething = YES;
                }
            }
        }
    }
    if (loadedSomething) {
        //TODO fix synchronousWrapper collapse bug
        if (self.entityDetail.galleries.count && !self.context.stamp) {
            //NSLog(@"\n\n\nGallery Attempt\n\n\n");
            id<STEntityDetailComponentFactory> factory = [[[STGalleryViewFactory alloc] init] autorelease];
            UIView* wrapper = [[[STSynchronousWrapper alloc] initWithDelegate:view componentFactory:factory 
                                                                 entityDetail:self.entityDetail 
                                                                     andFrame:CGRectMake(0, 0, 320, 200)] autorelease];
            [view appendChildView:wrapper];
        }
        if (self.context.stamp) {
            UIView* seeMore = [STActionsViewFactory moreInformationEntityDetail:self.entityDetail andDelegate:view];
            [view appendChildView:seeMore];
        }
        [view appendChildView:[[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 10)] autorelease]];
        NSSet* blacklist = [NSSet set];
        if (self.context.stamp) {
            blacklist = [NSSet setWithObject:self.context.stamp.user.userID];
        }
        id<STStampedBy> stampedBy = [[STStampedAPI sharedInstance] cachedStampedByForEntityID:self.entityDetail.entityID];
        if (stampedBy) {
            UIView* stampedByView = [[[STStampedByView alloc] initWithStampedBy:stampedBy 
                                                                      blacklist:blacklist 
                                                                       entityID:self.entityDetail.entityID
                                                                    andDelegate:delegate] autorelease];
            [view appendChildView:stampedByView];
        }
        else {
            STViewFactoryBlock factory = ^(STViewCreatorCallback callback) {
                [[STStampedAPI sharedInstance] stampedByForEntityID:self.entityDetail.entityID andCallback:^(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation) {
                    if (stampedBy) {
                        callback(^(id<STViewDelegate> delegate) {
                            return [[[STStampedByView alloc] initWithStampedBy:stampedBy 
                                                                     blacklist:blacklist 
                                                                      entityID:self.entityDetail.entityID
                                                                   andDelegate:delegate] autorelease];
                        });
                    }
                    else {
                        [Util warnWithMessage:@"Stamped by failed to load" andBlock:nil];
                        callback(^(id<STViewDelegate> delegate) {
                            return [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 10)] autorelease];
                        });
                    }
                }];
                
            };
            STSynchronousWrapper* stampedByWrapper = [[[STSynchronousWrapper alloc] initWithDelegate:view
                                                                                               frame:CGRectMake(0, 0, 320, 150)
                                                                                        factoryBlock:factory
                                                                                       andCompletion:nil] autorelease];
            [view appendChildView:stampedByWrapper];    
        }
        [view appendChildView:[[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 60)] autorelease]];
        return view;
    }
    else {
        return nil;
    }
}

- (void)main {
    NSOperationQueue* queue = [[[NSOperationQueue alloc] init] autorelease];
    for (NSString* key in [self.operations allKeys]) {
        NSOperation* operation = [self.operations objectForKey:key];
        id<STEntityDetailComponentFactory> factory = nil;
        if ([key isEqualToString:@"header"]) {
            factory = [[[STHeaderViewFactory alloc] initWithStyle:self.context.stamp ? @"StampDetail" : @"EntityDetail"] autorelease];
        }
        else if ([key isEqualToString:@"actions"]) {
            factory = [[[STActionsViewFactory alloc] init] autorelease];
        }
        else if ([key isEqualToString:@"metadata"]) {
            factory = [[[STMetadataViewFactory alloc] init] autorelease];
        }
        else if ([key isEqualToString:@"playlist"]) {
            factory = [[[STPlaylistViewFactory alloc] init] autorelease];
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
            @try {
                STViewCreator creator = ^(id<STViewDelegate> delegate) {
                    return [self createViewWithDelegate:delegate];
                };
                self.callback(creator);
            }
            @catch (NSException *exception) {
                [Util logOperationException:exception withMessage:nil];
            }
            @finally {
            }
        }
    });
}


@end

@implementation STEntityDetailViewFactory

@synthesize context = _context;

- (id)initWithContext:(STActionContext*)context {
    self = [super init];
    if (self) {
        _context = [context retain];
    }
    return self;
}

- (id)init {
    return [self initWithContext:[STActionContext context]];
}

- (NSOperation*)createViewWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock {
    STEntityDetailViewFactoryOperation* operation = [[[STEntityDetailViewFactoryOperation alloc] initWithEntityDetail:anEntityDetail context:self.context andCallbackBlock:aBlock] autorelease];
    return operation;
}

@end
