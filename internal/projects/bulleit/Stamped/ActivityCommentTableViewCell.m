//
//  ActivityCommentTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityCommentTableViewCell.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "UserImageView.h"
#import "Event.h"
#import "Comment.h"
#import "Entity.h"
#import "Stamp.h"
#import "User.h"

static const CGFloat kBadgeSize = 21.0;

@interface ActivityCommentCellView : UIView
  
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UILabel* mainLabel;
@property (nonatomic, readonly) UIImageView* badgeImageView;
@property (nonatomic, retain) CATextLayer* textLayer;
@property (nonatomic, readonly) UILabel* textLabel;
@end

@implementation ActivityCommentCellView

@synthesize highlighted = highlighted_;
@synthesize userImageView = userImageView_;
@synthesize mainLabel = mainLabel_;
@synthesize badgeImageView = badgeImageView_;
@synthesize textLayer = textLayer_;
@synthesize textLabel = textLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.autoresizingMask = (UIViewAutoresizingFlexibleWidth |
                             UIViewAutoresizingFlexibleHeight);
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 33, 33)];
    [self addSubview:userImageView_];
    [userImageView_ release];
    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kBadgeSize + 10,
                                   CGRectGetMaxY(userImageView_.frame) - kBadgeSize + 6,
                                   kBadgeSize, kBadgeSize);
    badgeImageView_ = [[UIImageView alloc] initWithFrame:badgeFrame];
    badgeImageView_.contentMode = UIViewContentModeCenter;
    [self addSubview:badgeImageView_];
    [badgeImageView_ release];
    
    self.textLayer = [[CATextLayer alloc] init];
    self.textLayer.truncationMode = kCATruncationEnd;
    self.textLayer.contentsScale = [[UIScreen mainScreen] scale];
    self.textLayer.fontSize = 12.0;
    self.textLayer.foregroundColor = [UIColor colorWithWhite:0.6 alpha:1.0].CGColor;
    self.textLayer.frame = CGRectMake(70, 13, 220, 16);
    NSDictionary* actions = [[NSDictionary alloc] initWithObjectsAndKeys:[NSNull null], @"contents", nil];
    self.textLayer.actions = actions;
    [actions release];
    [self.layer addSublayer:self.textLayer];
    [self.textLayer release];
    
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 27, 220, 20)];
    textLabel_.numberOfLines = 0;
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor colorWithWhite:0.15 alpha:1.0];
    textLabel_.lineBreakMode = UILineBreakModeWordWrap;
    textLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self addSubview:textLabel_];
    [textLabel_ release];
  }
  return self;
}

- (void)dealloc {
  self.textLayer = nil;
  [super dealloc];
}

@end

@implementation ActivityCommentTableViewCell

@synthesize event = event_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0, 0, self.contentView.bounds.size.width,
                                              self.contentView.bounds.size.height);
		customView_ = [[ActivityCommentCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)setEvent:(Event*)event {
  if (event == event_)
    return;

  [event_ release];
  event_ = [event retain];
  if (!event)
    return;

  customView_.userImageView.image = event.user.profileImage;
  if ([event.genre isEqualToString:@"mention"]) {
    customView_.badgeImageView.image = [UIImage imageNamed:@"activity_mention_badge"];
  } else {
    customView_.badgeImageView.image = [UIImage imageNamed:@"activity_chat_badge"];
  }
    
  NSString* user = @"";
  User* currentUser = [[AccountManager sharedManager] currentUser];
  if ([event.user.userID isEqualToString:currentUser.userID]) {
    user = @"You";
  } else {
    user = event.user.displayName;
  }
  NSString* actionString = @"";
  if ([event.genre isEqualToString:@"reply"]) {
    actionString = @"replied on";
  } else if ([event.genre isEqualToString:@"comment"]) {
    actionString = @"commented on";
  } else if ([event.genre isEqualToString:@"mention"]) {
    actionString = @"mentioned you on";
  }

  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);

  NSString* entityTitle = event.stamp.entityObject.title;
  NSString* full = [NSString stringWithFormat:@"%@ %@ %@", user, actionString, entityTitle];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
      (id)style, (id)kCTParagraphStyleAttributeName,
      (id)[UIColor colorWithWhite:0.6 alpha:1.0].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  if (![user isEqualToString:@"You"]) {
    [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  }
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:[full rangeOfString:entityTitle]];
  CFRelease(font);
  CFRelease(style);
  
  customView_.textLayer.string = string;
  [customView_ setNeedsDisplay];
  [string release];
  
  customView_.textLabel.text = event.comment.blurb;
  CGSize stringSize = [event.comment.blurb sizeWithFont:customView_.textLabel.font
                                      constrainedToSize:CGSizeMake(230, MAXFLOAT)
                                          lineBreakMode:UILineBreakModeWordWrap];
  CGRect textFrame = customView_.textLabel.frame;
  textFrame.size = stringSize;
  customView_.textLabel.frame = textFrame;
}

@end
