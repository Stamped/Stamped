//
//  ActivityTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "Event.h"
#import "UserImageView.h"

@class CATextLayer;

@interface ActivityTableViewCell : UITableViewCell {
 @protected
  UserImageView* userImageView_;
  CATextLayer* headerTextLayer_;
  UIImageView* disclosureArrowImageView_;
  UIImageView* badgeImageView_;
  UILabel* timestampLabel_;
  UILabel* addedStampsLabel_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;
- (void)invertColors:(BOOL)inverted;
- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color;

@property (nonatomic, retain) Event* event;

@end
