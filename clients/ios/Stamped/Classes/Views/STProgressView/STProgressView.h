//
//  STProgressView.h
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import <UIKit/UIKit.h>

@interface STProgressView : UIView {
    CALayer *_progressLayer;
}
@property(nonatomic,assign) CGFloat progress;

@end
