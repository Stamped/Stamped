//
//  STBlockUIView.h
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import <UIKit/UIKit.h>

typedef void(^STBlockUIViewDrawingHandler)(CGContextRef ctx, CGRect rect);

@interface STBlockUIView : UIView

@property(nonatomic,copy) STBlockUIViewDrawingHandler drawingHandler;

@end
