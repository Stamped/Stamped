//
//  STUnreadActivity.m
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import "STUnreadActivity.h"
#import "STStampedAPI.h"

static id __instance;

@implementation STUnreadActivity

+ (id)sharedInstance {
    
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

    }
    return self;
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}


#pragma mark - Updates

- (void)update {
    if (_updating || !LOGGED_IN) return;
    
    [[STStampedAPI sharedInstance] unreadCountWithCallback:^(id<STActivityCount> count, NSError *error, STCancellation *cancellation) {
        if (count && count.numberUnread.integerValue > 0) {
            [STEvents postEvent:EventTypeUnreadCountUpdated object:count.numberUnread];
        }
        _updating = NO;
    }];
    
}


#pragma mark - Notifications 

- (void)didEnterBackground:(NSNotification*)notification {
    
    [NSThread cancelPreviousPerformRequestsWithTarget:self selector:@selector(update) object:nil];
    
}

- (void)willEnterForeground:(NSNotification*)notification {
    
    [self performSelector:@selector(update) withObject:nil afterDelay:0.5];
    
}


@end
