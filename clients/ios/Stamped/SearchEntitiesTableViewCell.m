//
//  SearchEntitiesTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesTableViewCell.h"

#import "Entity.h"
#import "SearchResult.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"

@interface SearchEntitiesTableViewCell ()
@property (nonatomic, readonly) UIImageView* categoryImageView;
@property (nonatomic, readonly) UILabel* titleLabel;
@property (nonatomic, readonly) UILabel* subtitleLabel;
@property (nonatomic, readonly) UILabel* distanceLabel;
@property (nonatomic, readonly) UIImageView* locationImageView;
@end

@implementation SearchEntitiesTableViewCell

@synthesize searchResult = searchResult_;
@synthesize categoryImageView = categoryImageView_;
@synthesize titleLabel = titleLabel_;
@synthesize subtitleLabel = subtitleLabel_;
@synthesize distanceLabel = distanceLabel_;
@synthesize locationImageView = locationImageView_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    categoryImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(8, 0, 30, 32)];
    categoryImageView_.contentMode = UIViewContentModeBottomLeft;
    [self.contentView addSubview:categoryImageView_];
    [categoryImageView_ release];
    
    titleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 13, 241, 30)];
    titleLabel_.backgroundColor = [UIColor clearColor];
    titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:24];
    titleLabel_.textColor = [UIColor stampedBlackColor];
    titleLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:titleLabel_];
    [titleLabel_ release];
    
    subtitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 34, 241, 20)];
    subtitleLabel_.backgroundColor = [UIColor clearColor];
    subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
    subtitleLabel_.textColor = [UIColor stampedGrayColor];
    subtitleLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:subtitleLabel_];
    [subtitleLabel_ release];

    distanceLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    distanceLabel_.backgroundColor = [UIColor clearColor];
    distanceLabel_.textColor = [UIColor stampedLightGrayColor];
    distanceLabel_.highlightedTextColor = [UIColor whiteColor];
    distanceLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
    [self.contentView addSubview:distanceLabel_];
    [distanceLabel_ release];

    UIImage* locationImage = [UIImage imageNamed:@"small_location_icon"];
    UIImage* highlightedLocationImage = [Util whiteMaskedImageUsingImage:locationImage];
    locationImageView_ = [[UIImageView alloc] initWithImage:locationImage
                                           highlightedImage:highlightedLocationImage];
    [self.contentView addSubview:locationImageView_];
    [locationImageView_ release];
  }
  return self;
}

- (void)dealloc {
  self.searchResult = nil;
  [super dealloc];
}

- (void)setSearchResult:(SearchResult*)searchResult {
  if (searchResult_ != searchResult) {
    [searchResult_ release];
    searchResult_ = [searchResult retain];
    if (searchResult) {
      titleLabel_.text = searchResult.title;
      subtitleLabel_.text = searchResult.subtitle;
      categoryImageView_.image = searchResult.entitySearchCategoryImage;
      if (categoryImageView_.image)
        categoryImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:searchResult.entitySearchCategoryImage];
      if (searchResult.distance) {
        CGFloat miles = searchResult.distance.floatValue;
        if (miles < 2.0) {
          distanceLabel_.textColor = [UIColor colorWithRed:0.66 green:0.48 blue:0.8 alpha:1.0];
          locationImageView_.image = [UIImage imageNamed:@"small_location_icon_purple"];
        } else {
          distanceLabel_.textColor = [UIColor stampedLightGrayColor];
          locationImageView_.image = [UIImage imageNamed:@"small_location_icon"];
        }
        if (miles > 0.1)
          distanceLabel_.text = [NSString stringWithFormat:@"%.1f mi", miles];
        else
          distanceLabel_.text = [NSString stringWithFormat:@"%.0f ft", miles * 5280.0f];

        [distanceLabel_ sizeToFit];
        CGRect distanceFrame = distanceLabel_.frame;
        distanceFrame.origin.x = 311 - distanceFrame.size.width;
        distanceFrame.origin.y = 22;
        distanceLabel_.frame = distanceFrame;
        locationImageView_.frame = CGRectMake(CGRectGetMinX(distanceFrame) - CGRectGetWidth(locationImageView_.frame) - 3,
                                              CGRectGetMinY(distanceFrame) + 2, 
                                              CGRectGetWidth(locationImageView_.frame),
                                              CGRectGetHeight(locationImageView_.frame));
        distanceLabel_.hidden = NO;
        locationImageView_.hidden = NO;
      } else {
        distanceLabel_.hidden = YES;
        locationImageView_.hidden = YES;
      }
    }
  }
  [self.contentView setNeedsDisplay];
}

@end
