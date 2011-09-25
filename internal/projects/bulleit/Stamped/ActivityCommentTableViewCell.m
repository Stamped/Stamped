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

@interface ActivityCommentTableViewCell ()
- (void)invertColors:(BOOL)inverted;
- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color;

@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UILabel* mainLabel;
@property (nonatomic, readonly) UIImageView* badgeImageView;
@property (nonatomic, readonly) UIImageView* disclosureArrowImageView;
@property (nonatomic, readonly) CATextLayer* headerTextLayer;
@property (nonatomic, readonly) UILabel* textLabel;
@end

@implementation ActivityCommentTableViewCell

@synthesize userImageView = userImageView_;
@synthesize mainLabel = mainLabel_;
@synthesize badgeImageView = badgeImageView_;
@synthesize disclosureArrowImageView = disclosureArrowImageView_;
@synthesize headerTextLayer = headerTextLayer_;
@synthesize textLabel = textLabel_;

@synthesize event = event_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 33, 33)];
    userImageView_.backgroundColor = [UIColor whiteColor];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];
    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kBadgeSize + 10,
                                   CGRectGetMaxY(userImageView_.frame) - kBadgeSize + 6,
                                   kBadgeSize, kBadgeSize);
    badgeImageView_ = [[UIImageView alloc] initWithFrame:badgeFrame];
    badgeImageView_.contentMode = UIViewContentModeCenter;
    [self.contentView addSubview:badgeImageView_];
    [badgeImageView_ release];
    
    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 13, 210, 16);
    headerTextLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                           forKey:@"contents"];
    [self.contentView.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];
    
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(70, 27, 210, 20)];
    textLabel_.numberOfLines = 0;
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor colorWithWhite:0.15 alpha:1.0];
    textLabel_.highlightedTextColor = [UIColor whiteColor];
    textLabel_.lineBreakMode = UILineBreakModeWordWrap;
    textLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    [self.contentView addSubview:textLabel_];
    [textLabel_ release];
    
    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(290, 24, 8, 11)];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.image = disclosureImage;
    disclosureArrowImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self.contentView addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
  }
  return self;
}

- (void)invertColors:(BOOL)inverted {
  UIColor* color = inverted ? [UIColor whiteColor] : [UIColor stampedGrayColor];
  headerTextLayer_.string = [self headerAttributedStringWithColor:color];
  [self setNeedsDisplayInRect:headerTextLayer_.frame];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [self invertColors:selected];
}

- (void)setEvent:(Event*)event {
  if (event == event_)
    return;

  [event_ release];
  event_ = [event retain];
  if (!event)
    return;

  userImageView_.imageURL = event.user.profileImageURL;
  if ([event.genre isEqualToString:@"mention"]) {
    badgeImageView_.image = [UIImage imageNamed:@"activity_mention_badge"];
  } else {
    badgeImageView_.image = [UIImage imageNamed:@"activity_chat_badge"];
  }
  
  textLabel_.text = event.comment.blurb;
  CGSize stringSize = [event.comment.blurb sizeWithFont:textLabel_.font
                                      constrainedToSize:CGSizeMake(210, MAXFLOAT)
                                          lineBreakMode:UILineBreakModeWordWrap];
  CGRect textFrame = textLabel_.frame;
  textFrame.size = stringSize;
  textLabel_.frame = textFrame;
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  NSString* user = @"";
  User* currentUser = [[AccountManager sharedManager] currentUser];
  if ([event_.user.userID isEqualToString:currentUser.userID]) {
    user = @"You";
  } else {
    user = event_.user.screenName;
  }
  NSString* actionString = @"";
  if ([event_.genre isEqualToString:@"reply"]) {
    actionString = @"replied on";
  } else if ([event_.genre isEqualToString:@"comment"]) {
    actionString = @"commented on";
  } else if ([event_.genre isEqualToString:@"mention"]) {
    actionString = @"mentioned you on";
  }

  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSLog(@"Event: %@", event_);
  if (!event_.stamp)
    return nil;
  NSString* entityTitle = event_.stamp.entityObject.title;
  NSString* full = [NSString stringWithFormat:@"%@ %@ %@", user, actionString, entityTitle];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)color.CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  if (![user isEqualToString:@"You"]) {
    [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  }
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:[full rangeOfString:entityTitle]];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}

@end
