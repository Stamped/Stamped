//
//  PeopleTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleTableViewCell.h"

#import "MediumUserImageView.h"
#import "UIColor+Stamped.h"
#import "User.h"
#import "Util.h"

static const CGFloat kUserImageSize = 41.0;

@interface PeopleCellView : UIView

@property (nonatomic, readonly) MediumUserImageView* userImageView;
@property (nonatomic, readonly) UIImageView* stampImageView;
@property (nonatomic, readonly) UIImageView* arrowImageView;
@property (nonatomic, readonly) UILabel* fullNameLabel;
@property (nonatomic, readonly) UILabel* usernameLabel;
@end

@implementation PeopleCellView

@synthesize userImageView = userImageView_;
@synthesize stampImageView = stampImageView_;
@synthesize fullNameLabel = fullNameLabel_;
@synthesize usernameLabel = usernameLabel_;
@synthesize arrowImageView = arrowImageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.autoresizingMask = (UIViewAutoresizingFlexibleWidth |
                             UIViewAutoresizingFlexibleHeight);
    userImageView_ = [[MediumUserImageView alloc]
        initWithFrame:CGRectMake(10, 5, kUserImageSize, kUserImageSize)];
    [self addSubview:userImageView_];
    [userImageView_ release];
    
    stampImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(userImageView_.frame) + 16, 11, 14, 14)];
    [self addSubview:stampImageView_];
    [stampImageView_ release];
    
    fullNameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(
        CGRectGetMaxX(stampImageView_.frame) + 6, 8, 181, 21)];
    fullNameLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    fullNameLabel_.highlightedTextColor = [UIColor whiteColor];
    fullNameLabel_.textColor = [UIColor stampedBlackColor];
    fullNameLabel_.backgroundColor = [UIColor clearColor];
    [self addSubview:fullNameLabel_];
    [fullNameLabel_ release];
    
    usernameLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMinX(fullNameLabel_.frame), 27, 181, 17)];
    usernameLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    usernameLabel_.backgroundColor = [UIColor clearColor];
    usernameLabel_.textColor = [UIColor stampedLightGrayColor];
    usernameLabel_.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:usernameLabel_];
    [usernameLabel_ release];
    
    UIImage* arrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    UIImage* highlightedArrowImage = [Util whiteMaskedImageUsingImage:arrowImage];
    arrowImageView_ = [[UIImageView alloc] initWithImage:arrowImage
                                                    highlightedImage:highlightedArrowImage];
    arrowImageView_.contentMode = UIViewContentModeCenter;
    arrowImageView_.frame = CGRectMake(292, 21, 11, 11);
    [self addSubview:arrowImageView_];
    [arrowImageView_ release];
  }
  return self;
}

@end

@implementation PeopleTableViewCell

@synthesize user = user_;
@synthesize disclosureArrowHidden = disclosureArrowHidden_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault 
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0, 0, self.contentView.bounds.size.width,
                                        self.contentView.bounds.size.height);
    customView_ = [[PeopleCellView alloc] initWithFrame:customViewFrame];
    [self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)setDisclosureArrowHidden:(BOOL)hidden {
  if (disclosureArrowHidden_ == hidden)
    return;
  
  disclosureArrowHidden_ = hidden;
  customView_.arrowImageView.hidden = hidden;
}

- (void)setUser:(User*)user {
  if (user_ != user) {
    [user_ release];
    user_ = [user retain];
  }

  if (user) {
    customView_.userImageView.imageURL = user.profileImageURL;
    customView_.stampImageView.image = [user stampImageWithSize:StampImageSize14];
    customView_.usernameLabel.text = user.screenName;
    customView_.fullNameLabel.text = user.name;
  }
}

@end
