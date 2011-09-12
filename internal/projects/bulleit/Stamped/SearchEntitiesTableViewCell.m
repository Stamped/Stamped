//
//  SearchEntitiesTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesTableViewCell.h"

#import "Entity.h"
#import "Util.h"
#import "UIColor+Stamped.h"

@interface SearchEntitiesCellView : UIView

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, readonly) UIImageView* categoryImageView;
@property (nonatomic, readonly) UILabel* titleLabel;
@property (nonatomic, readonly) UILabel* subtitleLabel;
@end

@implementation SearchEntitiesCellView

@synthesize highlighted = highlighted_;
@synthesize categoryImageView = categoryImageView_;
@synthesize titleLabel = titleLabel_;
@synthesize subtitleLabel = subtitleLabel_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    categoryImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(8, 0, 30, 32)];
    categoryImageView_.contentMode = UIViewContentModeBottomLeft;
    [self addSubview:categoryImageView_];
    [categoryImageView_ release];
    
    titleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 13, 241, 30)];
    titleLabel_.backgroundColor = [UIColor clearColor];
    titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24];
    titleLabel_.textColor = [UIColor stampedBlackColor];
    titleLabel_.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:titleLabel_];
    [titleLabel_ release];
    
    subtitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 34, 241, 20)];
    subtitleLabel_.backgroundColor = [UIColor clearColor];
    subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    subtitleLabel_.textColor = [UIColor stampedGrayColor];
    subtitleLabel_.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:subtitleLabel_];
    [subtitleLabel_ release];
  }
  return self;
}

@end

@implementation SearchEntitiesTableViewCell

@synthesize entityObject = entityObject_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0.0, 0.0, self.contentView.bounds.size.width, self.contentView.bounds.size.height);
		customView_ = [[SearchEntitiesCellView alloc] initWithFrame:customViewFrame];
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
      customView_.categoryImageView.image = entityObject.largeCategoryImage;
      customView_.categoryImageView.highlightedImage =
          [Util whiteMaskedImageUsingImage:entityObject.largeCategoryImage];

    }
  }
}

@end
