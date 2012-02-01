//
//  STViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/5/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STViewController : UIViewController <UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UIView* shelfView;
@property (nonatomic, readonly) UIView* highlightView;

- (CGFloat)minimumShelfYPosition;
- (CGFloat)maximumShelfYPosition;

@end
