//
//  InboxTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "STStampFilterBar.h"

@class InboxCellView;
@class Entity;
@class PageDotsView;
@class Stamp;

extern NSString* const kInboxTableDidScrollNotification;

@interface InboxTableViewCell : UITableViewCell <UIScrollViewDelegate> {
 @private
  UIView* stacksBackgroundView_;
  BOOL stackExpanded_;
  UIButton* stackCollapseButton_;
  UIScrollView* userImageScrollView_;
  PageDotsView* pageDotsView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, readonly) InboxCellView* customView;
@property (nonatomic, assign) StampSortType sortType;

@end
