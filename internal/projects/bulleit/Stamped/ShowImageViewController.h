//
//  ShowImageViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface ShowImageViewController : UIViewController <UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UIImageView* imageView;
@property (nonatomic, retain) UIImage* image;

@end
