//
//  ActivityCreditTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class ActivityCreditCellView;
@class Event;

@interface ActivityCreditTableViewCell : UITableViewCell {
 @private
  ActivityCreditCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Event* event;
@property (nonatomic, readonly) UIImageView* tooltipImageView;

@end
