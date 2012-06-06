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

@interface STStampedByViewCell : STViewContainer

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
  self = [super initWithDelegate:delegate andFrame:CGRectMake(0, 0, 290, 0)];
  if (self) {
    entityID_ = [entityID retain];
    group_ = [group retain];
    scope_ = scope;
    CGFloat xOffset = 15;
    CGFloat yOffset = 10;
    NSString* formatString = nil;
    NSString* imagePath = nil;
    if (scope == STStampedAPIScopeFriends) {
      formatString = @"%@ friends";
      imagePath = @"scope_drag_inner_friends";
    }
    else if (scope == STStampedAPIScopeEveryone) {
      formatString = @"%@ users on Stamped";
      imagePath = @"scope_drag_inner_all";
    }
    UIImageView* iconView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imagePath]] autorelease];
    iconView.frame = [Util centeredAndBounded:iconView.frame.size inFrame:CGRectMake(xOffset, yOffset, 15, 15)];
    [self addSubview:iconView];
    NSString* countString = [NSString stringWithFormat:@"%d", group.count.integerValue];
    UILabel* headerText = [Util viewWithText:[NSString stringWithFormat:formatString, countString]
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
    
    UIView* viewAllButton = [Util tapViewWithFrame:self.frame target:self selector:@selector(viewAllClicked:) andMessage:nil];
    [self addSubview:viewAllButton];
    if (group.stampPreviews.count > 0 && imagesEnabled) {
      NSInteger limit = 7;
      UIView* images = [[[UIView alloc] initWithFrame:CGRectMake(xOffset, 0, self.frame.size.width - (2 * xOffset), 40)] autorelease];
      NSInteger i = 0;
      BOOL hasImages = NO;
      for (id<STStampPreview> stampPreview in group.stampPreviews) {
        if (![blacklist containsObject:stampPreview.user.userID]) {
          if (i >= limit) break;
          if (i == limit - 1) {
            
          }
          else {
            UIView* userImage = [Util profileImageViewForUser:stampPreview.user withSize:STProfileImageSize37];
            [Util reframeView:userImage withDeltas:CGRectMake(i*40, 0, 0, 0)];
            [images addSubview:userImage];
            UIView* buttonView = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageClicked:) andMessage:stampPreview];
            [images addSubview:buttonView];
            hasImages = YES;
          }
          i++;
        }
      }
      if (hasImages) {
        _hasImages = hasImages;
        [self appendChildView:images];
      }
    }
  }
  return self;
}

- (void)dealloc
{
  [group_ release];
  [entityID_ release];
  [super dealloc];
}

- (void)viewAllClicked:(id)nothing {
}
                                     
@end

@implementation STStampedByView

- (id)initWithStampedBy:(id<STStampedBy>)stampedBy blacklist:(NSSet*)blacklist entityID:(NSString*)entityID andDelegate:(id<STViewDelegate>)delegate
{
  self = [super initWithDelegate:delegate andFrame:CGRectMake(15, 0, 290, 0)];
  if (self) {
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
      [Util addGradientToLayer:self.layer 
                    withColors:[NSArray arrayWithObjects:[UIColor colorWithWhite:.95 alpha:1], [UIColor colorWithWhite:.90 alpha:1], nil]
                      vertical:YES];
    }
  }
  return self;
}

@end
