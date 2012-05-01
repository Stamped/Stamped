//
//  STStampCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STPageControl.h"

@interface STLegacyStampCell : UITableViewCell <UIScrollViewDelegate> {
@private
  UIView* stacksBackgroundView_;
  BOOL stackExpanded_;
  UIButton* stackCollapseButton_;
  UIScrollView* userImageScrollView_;
  STPageControl* pageControl_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

@end
