//
//  STImageView.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
@class STImageView;
@protocol STImageViewDelegate
- (void)STImageView:(STImageView*)imageView didLoadImage:(UIImage*)image;
@end

@interface STImageView : UIImageView
@property (nonatomic, copy) NSString* imageURL;
@property (nonatomic, assign) id<STImageViewDelegate> delegate;
@end
