//
//  STUnreadActivity.m
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import "STUnreadActivity.h"
#import "STStampedAPI.h"
#import "STEvents.h"
#import "STActionManager.h"
#import "STFacebook.h"

static id __instance;

@interface STUnreadActivity ()

@property (nonatomic, readwrite, retain) STCancellation* cancellation;

@end

@implementation STUnreadActivity

@synthesize count = _count;
@synthesize cancellation = _cancellation;

+ (STUnreadActivity*)sharedInstance {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        
        __instance = [[[self class] alloc] init];
        
    });
    
    return __instance;
    
}

- (id)init {
    if ((self = [super init])) {
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(willEnterForeground:) name:UIApplicationWillEnterForegroundNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didEnterBackground:) name:UIApplicationDidEnterBackgroundNotification object:nil];
        _count = 0;
    }
    return self;
}

- (void)dealloc {
    [_cancellation cancel];
    [_cancellation release];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}


#pragma mark - Updates

- (void)update {
    if (!LOGGED_IN || self.cancellation) return;
    
    self.cancellation = [[STStampedAPI sharedInstance] unreadCountWithCallback:^(id<STActivityCount> count, NSError *error, STCancellation *cancellation) {
        self.cancellation = nil;
        if (count.numberUnread.integerValue > 0) {
            self.count = count.numberUnread.integerValue;
        }
        [[STFacebook sharedInstance] auth];
        if (count.action) {
            [[STActionManager sharedActionManager] didChooseAction:count.action withContext:[STActionContext context]];
        }
    }];
    
}


- (void)setCount:(NSInteger)count {
    if (count != _count) {
        _count = count;
        [STEvents postEvent:EventTypeUnreadCountUpdated object:self];
    }
}

#pragma mark - Notifications 

- (void)didEnterBackground:(NSNotification*)notification {
    [self.cancellation cancel];
    self.cancellation = nil;
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(update) object:nil];
    
}

- (void)willEnterForeground:(NSNotification*)notification {
    
    [self performSelector:@selector(update) withObject:nil afterDelay:0.5];
    
}


@end
