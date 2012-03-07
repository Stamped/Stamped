//
//  STDetailScroller.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@protocol STGallery;

@interface STDetailScroller : UIScrollView

- (id)initWithGallery:(id<STGallery>)gallery;

@end
