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

@interface STGalleryView : UIScrollView

- (id)initWithGallery:(id<STGallery>)gallery andDelegate:(id<STViewDelegate>)delegate;

@end
