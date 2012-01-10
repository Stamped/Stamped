//
//  WrappingTextView.h
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreText/CoreText.h>

@interface WrappingTextView : UIView {
  CGPathRef textPath_;
}

- (id)initWithFrame:(CGRect)aRect text:(NSString*)text;

@property (nonatomic, assign) CGSize previewRectSize;
@property (nonatomic, retain) NSString* text;

@end
