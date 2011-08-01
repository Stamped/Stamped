//
//  ActivityCommentTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityCommentTableViewCell.h"

#import "UserImageView.h"
#import "Event.h"
#import "User.h"

static const CGFloat kBadgeSize = 21.0;

@interface ActivityCommentCellView : UIView
  
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UILabel* mainLabel;
@property (nonatomic, readonly) UIImageView* badgeImageView;
@end

@implementation ActivityCommentCellView

@synthesize highlighted = highlighted_;
@synthesize userImageView = userImageView_;
@synthesize mainLabel = mainLabel_;
@synthesize badgeImageView = badgeImageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectMake(15, 10, 33, 33)];
    [self addSubview:userImageView_];
    [userImageView_ release];
    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(userImageView_.frame) - kBadgeSize + 10,
                                   CGRectGetMaxY(userImageView_.frame) - kBadgeSize + 6,
                                   kBadgeSize, kBadgeSize);
    badgeImageView_ = [[UIImageView alloc] initWithFrame:badgeFrame];
    badgeImageView_.image = [UIImage imageNamed:@"activity_chat_badge"];
    badgeImageView_.contentMode = UIViewContentModeCenter;
    [self addSubview:badgeImageView_];
    [badgeImageView_ release];
  }
  return self;
}

- (void)dealloc {
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
    CGRect customViewFrame = CGRectMake(0.0, 0.0, self.contentView.bounds.size.width, self.contentView.bounds.size.height);
		customView_ = [[ActivityCommentCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)setEvent:(Event*)event {
  if (event != event_) {
    [event_ release];
    event_ = [event retain];
    if (event) {
      customView_.userImageView.image = event.user.profileImage;
    }
  }
}

@end
