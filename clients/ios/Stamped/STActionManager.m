//
//  STActionManager.m
//  Stamped
//
//  Created by Landon Judkins on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionManager.h"
#import "STActionMenuFactory.h"
#import "STViewDelegate.h"
#import "Util.h"
#import "STRdio.h"
#import "STMenuPopUp.h"
#import "STStampedActions.h"
#import "STSimpleAction.h"
#import "STStampedAPI.h"
#import "STRestKitLoader.h"
#import "STConfiguration.h"
#import "STActionUtil.h"
#import <MediaPlayer/MediaPlayer.h>

NSString* STActionManagerShowAllActionsKey = @"Actions.showAllActions";

@interface STActionManager () <STViewDelegate>

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;
- (BOOL)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;

@property (nonatomic, readonly, retain) NSOperationQueue* operationQueue;
@property (nonatomic, readonly, retain) NSMutableDictionary* sources;
@property (nonatomic, readwrite, retain) id<STStamp> stamp;
@property (nonatomic, readwrite, assign) BOOL locked;

@end

@implementation STActionManager

@synthesize operationQueue = _operationQueue;
@synthesize sources = _sources;
@synthesize actionsLocked = _actionsLocked;
@synthesize stamp = stamp_;
@synthesize locked = _locked;

static STActionManager* _singleton;

+ (void)initialize {
    _singleton = [[STActionManager alloc] init];
}

+ (STActionManager*)sharedActionManager {
    return _singleton;
}

- (id)init
{
    self = [super init];
    if (self) {
        _operationQueue = [[NSOperationQueue alloc] init];
        _sources = [[NSMutableDictionary alloc] init];
        [_sources setObject:[STRdio sharedRdio] forKey:@"rdio"];
        [_sources setObject:[STStampedActions sharedInstance] forKey:@"stamped"];
    }
    return self;
}

- (void)dealloc
{
    [_operationQueue release];
    [_sources release];
    [stamp_ release];
    [super dealloc];
}

- (void)setStampContext:(id<STStamp>)stamp {
    self.stamp = stamp;
}

- (BOOL)canHandleAction:(id<STAction>)action withContext:(STActionContext *)context{
    return [self didChooseAction:action withContext:context shouldExecute:NO];
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    // return YES;
    return [self handleSource:source withAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseAction:(id<STAction>)action withContext:(STActionContext *)context {
    [self didChooseAction:action withContext:context shouldExecute:YES];
}

- (BOOL)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
    if (!context.stamp) {
        context.stamp = self.stamp;
    }
    NSMutableArray* validSources = [NSMutableArray array];
    if (action.sources) {
        for (id<STSource> source in action.sources) {
            if ([self canHandleSource:source forAction:action.type withContext:context]) {
                [validSources addObject:source];
            }
        }
        if (flag) {
            if ([validSources count] > 1 && ![[action type] isEqualToString:@"listen"] ) {
                STActionMenuFactory* factory = [[[STActionMenuFactory alloc] init] autorelease];
                NSOperation* operation = [factory createViewWithAction:action sources:validSources andContext:context forBlock:^(STViewCreator init) {
                    if (init) {
                        UIView* view = init(self);
                        view.frame = [Util centeredAndBounded:view.frame.size inFrame:[[UIApplication sharedApplication] keyWindow].frame];
                        [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.3]];
                    }
                }];
                [self.operationQueue addOperation:operation];
            }
            else if ([validSources count] >= 1) {
                [self handleSource:[validSources objectAtIndex:0] withAction:action.type withContext:context shouldExecute:YES];
            }
        }
    }
    return [validSources count] > 0;
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
    [self handleSource:source withAction:action withContext:context shouldExecute:YES];
}

- (BOOL)handleSource:(id<STSource>)source withAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
    if (!context.stamp) {
        context.stamp = self.stamp;
    }
    BOOL handled = NO;
    if (self.locked) return NO;
    //if (flag) {
    //NSLog(@"didChooseSource:%@:%@ forAction:%@", source.source, source.sourceID, action);
    //NSLog(@"%@", source.completionData);
    
    //}
    if (!handled) {
        handled = [[STActionUtil sharedInstance] canHandleSource:source forAction:action withContext:context];
        if (handled && flag) {
            [[STActionUtil sharedInstance] didChooseSource:source forAction:action withContext:context];
            [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
        }
    }
    if (!handled && [action isEqualToString:@"watch"] && NO) {
        NSString* previewURL = [source.sourceData objectForKey:@"preview_url"];
        if (previewURL) {
            handled = YES;
            if (flag) {
                MPMoviePlayerViewController* controller = [[[MPMoviePlayerViewController alloc] initWithContentURL:[NSURL URLWithString:previewURL]] autorelease];
                [[Util currentNavigationController] presentMoviePlayerViewControllerAnimated:controller];
                [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
            }
        }
    }
    if (!handled) {
        id<STViewDelegate> sourceObject = [self.sources objectForKey:source.source];
        if (sourceObject != nil && 
            [sourceObject respondsToSelector:@selector(canHandleSource:forAction:withContext:)] &&
            [sourceObject canHandleSource:source forAction:action withContext:context] &&
            [sourceObject respondsToSelector:@selector(didChooseSource:forAction:withContext:)]) {
            handled = TRUE;
            if (flag) {
                [sourceObject didChooseSource:source forAction:action withContext:context];
                [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
            }
        }
    }
    if (!handled && source.endpoint) {
        handled = [[STStampedAPI sharedInstance] canHandleSource:source forAction:action withContext:context];
        if (handled && flag) {
            [[STStampedAPI sharedInstance] didChooseSource:source forAction:action withContext:context];
            [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
        }
    }
    if (!handled && (source.link && ![action isEqualToString:@"listen"])) {
        handled = TRUE;
        if (flag) {
            NSURL* url = [NSURL URLWithString:source.link];
            if ([url.scheme isEqualToString:@"tel"]) {
                [Util confirmWithMessage:[NSString stringWithFormat:@"Are you sure?"]
                                  action:@"Call"
                             destructive:NO
                               withBlock:^(BOOL result) {
                                   if (result) {
                                       [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
                                       [[UIApplication sharedApplication] openURL:url];
                                   }
                               }];
            }
            else {
                [[STStampedAPI sharedInstance] handleCompletionWithSource:source action:action andContext:context];
                [[UIApplication sharedApplication] openURL:url];
            }
        }
    }
    return handled;
}

+ (void)setupConfigurations {
    [STConfiguration addFlag:NO forKey:STActionManagerShowAllActionsKey];
}

- (BOOL)lock {
    if (self.locked) {
        return NO;
    }
    else {
        self.locked = YES;
        return YES;
    }
}

- (BOOL)unlock {
    if (!self.locked) {
        return NO;
    }
    else {
        self.locked = NO;
        return YES;
    }
}

+ (BOOL)lock {
    BOOL result = [[STActionManager sharedActionManager] lock];
    if (!result) {
        [STStampedAPI logError:@"Concurrent action: could not get lock."];
    }
    return result;
}

+ (BOOL)unlock {
    BOOL result = [[STActionManager sharedActionManager] unlock];
    if (!result) {
        [STStampedAPI logError:@"Concurrent action: could not release lock."];
    }
    return result;
}

@end
