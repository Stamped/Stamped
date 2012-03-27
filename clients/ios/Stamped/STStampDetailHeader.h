//
//  STStampDetailHeader.h
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STStampDetailHeader : UIControl

@property (nonatomic, readonly) UIImageView* arrowImageView;
@property (nonatomic, readonly) UILabel* subtitleLabel;
@property (nonatomic, readonly) UIImageView* categoryImageView;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* title;

@end
