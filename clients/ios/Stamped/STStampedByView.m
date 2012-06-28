//
//  STStampedByView.m
//  Stamped
//
//  Created by Landon Judkins on 4/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedByView.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STStampedAPI.h"
#import <QuartzCore/QuartzCore.h>
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STTableViewController.h"
#import "STStampsViewSource.h"
#import "STButton.h"
#import "STUsersViewController.h"

@interface STStampedByViewCell : UIView

- (id)initWithStampedByGroup:(id<STStampedByGroup>)group 
               imagesEnabled:(BOOL)imagesEnabled
                       scope:(STStampedAPIScope)scope 
                   blacklist:(NSSet*)blacklist
                    entityID:(NSString*)entityID
                 andDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, readonly, assign) BOOL hasImages;
@property (nonatomic, readonly, retain) id<STStampedByGroup> group;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;
@property (nonatomic, readonly, retain) NSString* entityID;

@end

@implementation STStampedByViewCell

@synthesize hasImages = _hasImages;
@synthesize group = group_;
@synthesize scope = scope_;
@synthesize entityID = entityID_;

- (void)userImageClicked:(id<STStampPreview>)stampPreview {
    STActionContext* context = [STActionContext contextInView:self];
    id<STAction> action = [STStampedActions actionViewStamp:stampPreview.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (id)initWithStampedByGroup:(id<STStampedByGroup>)group 
               imagesEnabled:(BOOL)imagesEnabled 
                       scope:(STStampedAPIScope)scope 
                   blacklist:(NSSet*)blacklist 
                    entityID:(NSString*)entityID
                 andDelegate:(id<STViewDelegate>)delegate {
    self = [super initWithFrame:CGRectMake(0, 0, 290, 0)];
    if (self) {
        BOOL shouldShowArrow = YES;
        entityID_ = [entityID retain];
        group_ = [group retain];
        scope_ = scope;
        CGFloat xOffset = 15;
        CGFloat yOffset = 10;
        NSString* formatString = nil;
        NSString* imagePath = nil;
        if (scope == STStampedAPIScopeFriends) {
            formatString = @"%@ friend%@";
            imagePath = @"TEMP_friends_icon";
        }
        else if (scope == STStampedAPIScopeEveryone) {
            formatString = @"%@ user%@ on Stamped";
            imagePath = @"TEMP_everyone_icon";
        }
        UIImageView* iconView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imagePath]] autorelease];
        iconView.frame = [Util centeredAndBounded:iconView.frame.size inFrame:CGRectMake(xOffset, yOffset, 15, 15)];
        [self addSubview:iconView];
        NSString* countString = [NSString stringWithFormat:@"%d", group.count.integerValue];
        UILabel* headerText = [Util viewWithText:[NSString stringWithFormat:formatString, countString, group.count.integerValue == 1 ? @"" : @"s"]
                                            font:[UIFont stampedSubtitleFont]
                                           color:[UIColor stampedGrayColor]
                                            mode:UILineBreakModeClip
                                      andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
        [Util reframeView:headerText withDeltas:CGRectMake(CGRectGetMaxX(iconView.frame)+7,
                                                           yOffset,
                                                           0,
                                                           0)];
        [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, CGRectGetMaxY(headerText.frame)+yOffset)];
        [self addSubview:headerText];
        
        if (group.stampPreviews.count > 0 && imagesEnabled) {
            NSInteger limit = 6;
            UIView* images = [[[UIView alloc] initWithFrame:CGRectMake(xOffset, 0, self.frame.size.width - (2 * xOffset), 40)] autorelease];
            NSInteger i = 0;
            CGFloat imageSpacing = 40;
            BOOL hasImages = NO;
            for (id<STStampPreview> stampPreview in group.stampPreviews) {
                if (![blacklist containsObject:stampPreview.user.userID]) {
                    if (i >= limit) break;
                    if (i == limit - 1) {
                        shouldShowArrow = NO;
                    }
                    UIView* userImage = [Util profileImageViewForUser:stampPreview.user withSize:37];
                    [Util reframeView:userImage withDeltas:CGRectMake(i * imageSpacing, 0, 0, 0)];
                    [images addSubview:userImage];
                    UIView* buttonView = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:stampPreview];
                    [images addSubview:buttonView];
                    hasImages = YES;
                    i++;
                }
            }
            if (hasImages) {
                CGRect imagesFrame = images.frame;
                imagesFrame.size.width = i * imageSpacing;
                images.frame = imagesFrame;
                _hasImages = hasImages;
                [Util appendView:images toParentView:self];
            }
        }
        CGRect buttonFrame = self.frame;
        UIView* views[2];
        for (NSInteger i = 0; i < 2; i++) {
            UIView* view = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
            if (i == 0) {
                view.backgroundColor = [UIColor clearColor];
            }
            else {
                [Util addGradientToLayer:view.layer withColors:[UIColor stampedButtonGradient] vertical:YES];
            }
            views[i] = view;
        }
        STButton* button = [[[STButton alloc] initWithFrame:buttonFrame normalView:views[0] activeView:views[1] target:self andAction:@selector(viewAllClicked:)] autorelease];
        button.layer.cornerRadius = 2;
        button.clipsToBounds = YES;
        [self insertSubview:button atIndex:0];
        
        UIImageView* arrowView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"TEMP_eDetailBox_arrow_right"]] autorelease];
        arrowView.frame = [Util centeredAndBounded:arrowView.frame.size inFrame:CGRectMake(268, 0, arrowView.frame.size.width, self.frame.size.height)];
        [self addSubview:arrowView];
    }
    return self;
}

- (void)dealloc {
    [group_ release];
    [entityID_ release];
    [super dealloc];
}

- (void)viewAllClicked:(id)nothing {
    NSMutableArray* userIDs = [NSMutableArray array];
    NSMutableDictionary* mapping = [NSMutableDictionary dictionary];
    for (id<STStampPreview> preview in [self.group stampPreviews]) {
        NSString* userID = preview.user.userID;
        if (userID) {
            [userIDs addObject:userID];
            if (preview.stampID) {
                [mapping setObject:preview.stampID forKey:userID];
            }
        }
    }
    STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
    controller.userIDToStampID = mapping;
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

@end

@implementation STStampedByView

- (id)initWithStampedBy:(id<STStampedBy>)stampedBy blacklist:(NSSet*)blacklist entityID:(NSString*)entityID andDelegate:(id<STViewDelegate>)delegate {
    self = [super initWithDelegate:delegate andFrame:CGRectMake(15, 0, 290, 0)];
    if (self) {
        //self.clipsToBounds = YES;
        NSMutableArray* array = [NSMutableArray array];
        //TODO determine hasImages purpose or remove
        BOOL hasImages = NO;
        if (stampedBy.friends.count.integerValue) {
            STStampedByViewCell* child = [[[STStampedByViewCell alloc] initWithStampedByGroup:stampedBy.friends 
                                                                                imagesEnabled:YES
                                                                                        scope:STStampedAPIScopeFriends
                                                                                    blacklist:blacklist 
                                                                                     entityID:entityID
                                                                                  andDelegate:self] autorelease];
            [array addObject:child];
            hasImages = hasImages | child.hasImages;
        }
        if (stampedBy.everyone.count.integerValue) {
            STStampedByViewCell* child = [[[STStampedByViewCell alloc] initWithStampedByGroup:stampedBy.everyone
                                                                                imagesEnabled:!hasImages
                                                                                        scope:STStampedAPIScopeEveryone
                                                                                    blacklist:blacklist
                                                                                     entityID:entityID
                                                                                  andDelegate:self] autorelease];
            [array addObject:child];
            hasImages = hasImages | child.hasImages;
        }
        if (array.count) {
            UILabel* header = [Util viewWithText:@"Stamped By"
                                            font:[UIFont stampedFontWithSize:12]
                                           color:[UIColor stampedDarkGrayColor]
                                            mode:UILineBreakModeClip
                                      andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
            [Util reframeView:header withDeltas:CGRectMake(15, 0, 0, 10)];
            [self appendChildView:header];
            BOOL first = YES;
            UIImage* image = [UIImage imageNamed:@"eDetailBox_line"];
            for (STStampedByViewCell* cell in array) {
                if (!first) {
                    UIView* bar = [[[UIImageView alloc] initWithImage:image] autorelease];
                    [Util reframeView:bar withDeltas:CGRectMake(1, 0, 0, 0)];
                    [self appendChildView:bar];
                }
                [self appendChildView:cell];
                first = NO;
            }
            self.layer.borderWidth = 1;
            self.layer.borderColor = [UIColor colorWithWhite:.9 alpha:1].CGColor;
            self.layer.cornerRadius = 2;
            self.layer.shadowOffset = CGSizeMake(0,1);
            self.layer.shadowOpacity = .1;
            self.layer.shadowRadius = 1;
            self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
            [Util addGradientToLayer:self.layer 
                          withColors:[UIColor stampedLightGradient]
                            vertical:YES];
        }
    }
    return self;
}

@end
