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
#import "Util.h"
#import "UIColor+Stamped.h"

static const CGFloat kBadgeSize = 21.0;

@interface ActivityCommentCellView : UIView
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;

@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UILabel* mainLabel;
@property (nonatomic, readonly) UIImageView* badgeImageView;
@property (nonatomic, readonly) UIImageView* disclosureArrowImageView;
@property (nonatomic, readonly) CATextLayer* headerTextLayer;
@property (nonatomic, readonly) UILabel* textLabel;
@end

@implementation ActivityCommentCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize userImageView = userImageView_;
@synthesize mainLabel = mainLabel_;
@synthesize badgeImageView = badgeImageView_;
@synthesize disclosureArrowImageView = disclosureArrowImageView_;
@synthesize headerTextLayer = headerTextLayer_;
@synthesize textLabel = textLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.autoresizingMask = (UIViewAutoresizingFlexibleWidth |
                             UIViewAutoresizingFlexibleHeight);
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 33, 33)];
    userImageView_.backgroundColor = [UIColor whiteColor];
    [self addSubview:userImageView_];
    [userImageView_ release];
    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kBadgeSize + 10,
                                   CGRectGetMaxY(userImageView_.frame) - kBadgeSize + 6,
                                   kBadgeSize, kBadgeSize);
    badgeImageView_ = [[UIImageView alloc] initWithFrame:badgeFrame];
    badgeImageView_.contentMode = UIViewContentModeCenter;
    [self addSubview:badgeImageView_];
    [badgeImageView_ release];
    
    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 13, 210, 16);
    headerTextLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                           forKey:@"contents"];
    [self.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];
    
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 27, 210, 20)];
    textLabel_.numberOfLines = 0;
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor colorWithWhite:0.15 alpha:1.0];
    textLabel_.highlightedTextColor = [UIColor whiteColor];
    textLabel_.lineBreakMode = UILineBreakModeWordWrap;
    textLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self addSubview:textLabel_];
    [textLabel_ release];
    
    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(290, 24, 8, 11)];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.image = disclosureImage;
    disclosureArrowImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
  }
  return self;
}

- (void)invertColors:(BOOL)inverted {
  NSMutableAttributedString* headerAttributedString =
      [[NSMutableAttributedString alloc] initWithAttributedString:headerTextLayer_.string];
  CGColorRef color = inverted ? [UIColor whiteColor].CGColor :
      [UIColor stampedGrayColor].CGColor;
  [headerAttributedString setAttributes:
   [NSDictionary dictionaryWithObject:(id)color 
                               forKey:(id)kCTForegroundColorAttributeName] 
                                  range:NSMakeRange(0, headerAttributedString.length)];
  headerTextLayer_.string = headerAttributedString;
  [headerAttributedString release];
  [self setNeedsDisplayInRect:headerTextLayer_.frame];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  selected_ = selected;
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted {
  highlighted_ = highlighted;
  [self invertColors:highlighted];
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

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
}

- (void)setEvent:(Event*)event {
  if (event == event_)
    return;

  [event_ release];
  event_ = [event retain];
  if (!event)
    return;

  customView_.userImageView.imageURL = event.user.profileImageURL;
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
    user = event.user.screenName;
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
      (id)[UIColor stampedGrayColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  if (![user isEqualToString:@"You"]) {
    [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  }
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:[full rangeOfString:entityTitle]];
  CFRelease(font);
  CFRelease(style);
  
  customView_.headerTextLayer.string = string;
  [customView_ setNeedsDisplay];
  [string release];
  
  customView_.textLabel.text = event.comment.blurb;
  CGSize stringSize = [event.comment.blurb sizeWithFont:customView_.textLabel.font
                                      constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                          lineBreakMode:UILineBreakModeWordWrap];
  CGRect textFrame = customView_.textLabel.frame;
  textFrame.size = stringSize;
  customView_.textLabel.frame = textFrame;
}

@end
