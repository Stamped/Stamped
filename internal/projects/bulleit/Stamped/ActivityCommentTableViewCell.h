//
//  ActivityCommentTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class ActivityCommentCellView;
@class Event;

@interface ActivityCommentTableViewCell : UITableViewCell {
 @private
  ActivityCommentCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Event* event;

@end
