//
//  ShowImageViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class STImageView;

@interface ShowImageViewController : UIViewController <UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet STImageView* imageView;
@property (nonatomic, retain) UIImage* image;
@property (nonatomic, copy) NSString* imageURL;

@end
