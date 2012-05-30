//
//  STStampTitleView.h
//  Stamped
//
//  Created by Devin Doty on 5/29/12.
//
//

#import <UIKit/UIKit.h>
#import <CoreText/CoreText.h>

@interface STStampTitleView : UIView {
    CTFrameRef _frame;
    CTFramesetterRef _framesetter;
}
@property(nonatomic,copy) NSString *title;

- (void)frameSize;

@end
