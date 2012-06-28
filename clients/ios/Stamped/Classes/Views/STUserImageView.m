//
//  STUserImageView.m
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserImageView.h"
#import "STImageCache.h"
#import "STStampedAPI.h"
#import <QuartzCore/QuartzCore.h>
#import "STActionManager.h"
#import "STStampedActions.h"

@interface STUserImageView ()

@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readonly, retain) UITapGestureRecognizer* recognizer;
@property (nonatomic, readwrite, retain) id<STAction> action;
@property (nonatomic, readwrite, retain) STActionContext* context;
@property (nonatomic, readwrite, assign) BOOL observing;

@end

@implementation STUserImageView

@synthesize user = _user;
@synthesize cancellation = _cancellation;
@synthesize recognizer = _recognizer;
@synthesize action = _action;
@synthesize context = _context;
@synthesize observing = _observing;

- (id)initWithSize:(CGFloat)size {
    self = [super initWithFrame:CGRectMake(0, 0, size, size)];
    if (self) {
        self.layer.borderWidth = 1.5;
        self.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
        self.layer.borderColor = [UIColor whiteColor].CGColor;
        self.layer.shadowOffset = CGSizeMake(0,1);
        self.layer.shadowOpacity = .3;
        self.layer.shadowRadius = 1;
        self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
        _recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(clicked:)];
        //_recognizer.enabled = NO;
        self.userInteractionEnabled = YES;
        [self addGestureRecognizer:_recognizer];
    }
    return self;
}

- (id)initWithUser:(id<STUser>)user withSize:(CGFloat)size {
    self = [self initWithSize:size];
    [self setupWithUser:user viewAction:NO];
    return self;
}

- (void)dealloc
{
    if (_observing) {
        [[NSNotificationCenter defaultCenter] removeObserver:self];
    }
    [_user release];
    [_cancellation cancel];
    [_cancellation release];
    [_recognizer release];
    [_action release];
    [_context release];
    [super dealloc];
}

- (void)setAction:(id<STAction>)action withContext:(STActionContext *)context {
    if (action) {
        self.recognizer.enabled = YES;
    }
    else {
        self.recognizer.enabled = NO;
    }
    if (!context) {
        self.context = [STActionContext context];
    }
    self.action = action;
    self.context = context;
}

- (void)clearAction {
    [self setAction:nil withContext:nil];
}

- (void)clicked:(id)notImportant {
    id<STAction> action = self.action;
    if (action && self.context) {
        [[STActionManager sharedActionManager] didChooseAction:action withContext:self.context];
    }
}

- (void)updateUser:(id)notImportant {
    [self setupWithUser:self.user viewAction:NO];
}

- (void)setupWithUser:(id<STUser>)user viewAction:(BOOL)action {
    if (self.observing) {
        [[NSNotificationCenter defaultCenter] removeObserver:self];
    }
    self.observing = NO;
    CGFloat size = self.frame.size.width;
    [self.cancellation cancel];
    self.cancellation = nil;
    self.user = user;
    self.image = nil;
    if (user) {
        size = size * [UIScreen mainScreen].scale;
        STProfileImageSize profileSize = STProfileImageSize24;
        if (size > profileSize) {
            profileSize = STProfileImageSize48;
            if (size > profileSize) {
                profileSize = STProfileImageSize60;
                if (size > profileSize) {
                    profileSize = STProfileImageSize96;
                    if (size > profileSize) {
                        profileSize = STProfileImageSize144;
                    }
                }
            }
        }
        UIImage* cachedImage = nil;
        if (IS_CURRENT_USER(user.userID)) {
            self.observing = YES;
            [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(updateUser:) name:STStampedAPIUserUpdatedNotification object:nil];
            cachedImage = [[STStampedAPI sharedInstance] currentUserImageForSize:profileSize];
        }
        if (!cachedImage) {
            cachedImage = [[STImageCache sharedInstance] cachedUserImageForUser:user size:profileSize];
        }
        if (cachedImage) {
            self.image = cachedImage;
        }
        else {
            self.cancellation = [[STImageCache sharedInstance] userImageForUser:user size:profileSize andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                if (self.user == user) {
                    self.cancellation = nil;
                    self.image = image;
                }
            }];
        }
    }
    if (action) {
        if (user) {
            STActionContext* context = [STActionContext context];
            id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
            [self setAction:action withContext:context];
        }
        else {
            [self clearAction];
        }
    }
}

@end
