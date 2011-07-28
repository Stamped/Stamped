//
//  CreateStampTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampTableViewCell.h"

#import "Entity.h"
#import "Util.h"

@interface CreateStampCellView : UIView

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, retain) UIImageView* categoryImageView;
@property (nonatomic, retain) UILabel* titleLabel;
@property (nonatomic, retain) UILabel* subtitleLabel;
@end

@implementation CreateStampCellView

@synthesize highlighted = highlighted_;
@synthesize categoryImageView = categoryImageView_;
@synthesize titleLabel = titleLabel_;
@synthesize subtitleLabel = subtitleLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.categoryImageView = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 27, 32)];
    self.categoryImageView.contentMode = UIViewContentModeBottomRight;
    [self addSubview:self.categoryImageView];
    [self.categoryImageView release];
    
    self.titleLabel = [[UILabel alloc] initWithFrame:CGRectMake(36, 13, 241, 30)];
    self.titleLabel.backgroundColor = [UIColor clearColor];
    self.titleLabel.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24];
    self.titleLabel.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
    self.titleLabel.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:self.titleLabel];
    [self.titleLabel release];
    
    self.subtitleLabel = [[UILabel alloc] initWithFrame:CGRectMake(36, 34, 241, 20)];
    self.subtitleLabel.backgroundColor = [UIColor clearColor];
    self.subtitleLabel.font = [UIFont fontWithName:@"Helvetica" size:12];
    self.subtitleLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    self.subtitleLabel.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:self.subtitleLabel];
    [self.subtitleLabel release];
  }
  return self;
}

- (void)dealloc {
  self.categoryImageView = nil;
  self.titleLabel = nil;
  self.subtitleLabel = nil;
  [super dealloc];
}

@end

@implementation CreateStampTableViewCell

@synthesize entityObject = entityObject_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0.0, 0.0, self.contentView.bounds.size.width, self.contentView.bounds.size.height);
		customView_ = [[CreateStampCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)dealloc {
  self.entityObject = nil;
  [super dealloc];
}

- (void)setEntityObject:(Entity*)entityObject {
  if (entityObject != entityObject_) {
    [entityObject_ release];
    entityObject_ = [entityObject retain];
    if (entityObject) {
      customView_.titleLabel.text = entityObject.title;
      customView_.subtitleLabel.text = entityObject.subtitle;
      customView_.categoryImageView.image = entityObject.categoryImage;
      customView_.categoryImageView.highlightedImage =
          [Util whiteMaskedImageUsingImage:entityObject.categoryImage];

    }
  }
}

@end
