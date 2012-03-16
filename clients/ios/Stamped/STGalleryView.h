//
//  STGalleryView.h
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STGallery.h"
#import "STViewDelegate.h"

@interface STGalleryView : UIView <UIScrollViewDelegate>

- (id)initWithGallery:(id<STGallery>)gallery images:(NSArray*)images andDelegate:(id<STViewDelegate>)delegate;

@end
