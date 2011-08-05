//
//  InboxTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class InboxCellView;
@class Entity;

extern NSString* kInboxTableDidScrollNotification;

@interface InboxTableViewCell : UITableViewCell {
 @private  
  InboxCellView* customView_;
  UIView* stacksBackgroundView_;
  BOOL stackExpanded_;
  UIButton* stackCollapseButton_;
  UIScrollView* userImageScrollView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Entity* entityObject;

@end
