//
//  WrappingTextView.h
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreText/CoreText.h>

@interface WrappingTextView : UIView {
  CGSize previewRectSize;
  NSUInteger frameCount;
  NSString* text;
  CGFloat contentHeight;
  CGPathRef textPath_;
}

- (id)initWithFrame:(CGRect)aRect text:(NSString*)text;

@property (nonatomic, assign) CGSize previewRectSize;
@property (nonatomic, retain) NSString* text;

@end
